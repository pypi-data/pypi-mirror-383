import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

window.CLIPSPACE_TO_OSS_MAP = window.CLIPSPACE_TO_OSS_MAP || {};

// ═══════════════════════════════════════════════════════════════════════════
// 工具函数：查找 clipspace 文件名对应的 OSS URL
// ═══════════════════════════════════════════════════════════════════════════
function findOssUrl(filename) {
    return window.CLIPSPACE_TO_OSS_MAP[filename]
        || window.CLIPSPACE_TO_OSS_MAP[`${filename} [input]`]
        || window.CLIPSPACE_TO_OSS_MAP[`${filename} [output]`];
}

// ═══════════════════════════════════════════════════════════════════════════
// 工具函数：替换 clipspace URL 为 OSS URL
// ═══════════════════════════════════════════════════════════════════════════
function replaceClipspaceUrl(urlString) {
    if (!urlString || typeof urlString !== 'string') return urlString;
    if (!urlString.includes('/view?') || !urlString.includes('clipspace')) return urlString;

    try {
        const url = new URL(urlString, window.location.origin);
        const filename = url.searchParams.get('filename');
        const subfolder = url.searchParams.get('subfolder');

        if (subfolder === 'clipspace' && filename) {
            const ossUrl = findOssUrl(filename);
            if (ossUrl) {
                url.searchParams.set('filename', ossUrl);
                url.searchParams.set('subfolder', '');
                return url.pathname + url.search;
            }
        }
    } catch (e) {
        console.error('[BizyDraft] Error replacing clipspace URL:', e);
    }

    return urlString;
}

// ═══════════════════════════════════════════════════════════════════════════
// 拦截图片加载请求，将 clipspace URL 替换为 OSS URL
// ═══════════════════════════════════════════════════════════════════════════
(function interceptImageLoading() {
    const originalSrcDescriptor = Object.getOwnPropertyDescriptor(Image.prototype, 'src');

    Object.defineProperty(Image.prototype, 'src', {
        get() {
            return originalSrcDescriptor.get.call(this);
        },
        set(value) {
            const modifiedValue = replaceClipspaceUrl(value);
            if (modifiedValue !== value) {
                console.log('[BizyDraft Image] Redirected:', value, '->', modifiedValue);
            }
            originalSrcDescriptor.set.call(this, modifiedValue);
        },
        configurable: true
    });

    const originalSetAttribute = HTMLImageElement.prototype.setAttribute;
    HTMLImageElement.prototype.setAttribute = function(name, value) {
        if (name === 'src') {
            const modifiedValue = replaceClipspaceUrl(value);
            if (modifiedValue !== value) {
                console.log('[BizyDraft setAttribute] Redirected to OSS');
            }
            return originalSetAttribute.call(this, name, modifiedValue);
        }
        return originalSetAttribute.call(this, name, value);
    };

    console.log('[BizyDraft] Image interceptor installed');
})();

// ═══════════════════════════════════════════════════════════════════════════
// 拦截上传响应，保存映射并篡改返回值
// ═══════════════════════════════════════════════════════════════════════════
const originalFetchApi = api.fetchApi;
api.fetchApi = async function(url, options) {
    const response = await originalFetchApi.call(this, url, options);

    const isUploadApi = url === '/upload/image' || url === '/upload/mask'
                     || url === '/api/upload/image' || url === '/api/upload/mask';

    if (!isUploadApi || !response.ok) {
        return response;
    }

    try {
        const data = await response.clone().json();

        // 检查是否是 OSS 上传响应
        const isOssUpload = data.subfolder?.includes('http://') || data.subfolder?.includes('https://')
                         || data.name?.startsWith('http://') || data.name?.startsWith('https://');

        if (!isOssUpload) {
            return response;
        }

        // 构造完整的 OSS URL
        const ossUrl = data.subfolder?.includes('http')
            ? `${data.subfolder}/${data.name}`
            : data.name;

        // 处理映射逻辑
        let finalUrl = ossUrl;

        if (options?.body instanceof FormData) {
            const imageFile = options.body.get('image');
            if (imageFile?.name) {
                const filename = imageFile.name;
                const idMatch = filename.match(/(\d+)/);
                const baseId = idMatch?.[1];

                console.log('[BizyDraft Upload]', url, '-', filename, `(${imageFile.size} bytes)`);
                console.log('[BizyDraft Upload] Backend response:', data.name);

                // 第一次 /upload/mask 的结果是涂改后的完整图片
                if (baseId && url.includes('/upload/mask')) {
                    const firstMaskKey = `__FIRST_MASK_${baseId}__`;

                    if (!window.CLIPSPACE_TO_OSS_MAP[firstMaskKey]) {
                        // 首次 mask 上传，保存到所有变体
                        window.CLIPSPACE_TO_OSS_MAP[firstMaskKey] = ossUrl;
                        finalUrl = ossUrl;

                        [`clipspace-mask-${baseId}.png`, `clipspace-paint-${baseId}.png`,
                         `clipspace-painted-${baseId}.png`, `clipspace-painted-masked-${baseId}.png`
                        ].forEach(v => window.CLIPSPACE_TO_OSS_MAP[v] = ossUrl);

                        console.log('[BizyDraft Upload] ✅ First mask upload, saved to all variants');
                    } else {
                        // 后续 mask 上传，使用首次的 URL
                        finalUrl = window.CLIPSPACE_TO_OSS_MAP[firstMaskKey];
                        console.log('[BizyDraft Upload] ⏭️  Later mask upload, using first URL');
                    }
                } else if (baseId) {
                    // /upload/image 的上传，如果已有 mask 则使用 mask 的 URL
                    const firstMaskUrl = window.CLIPSPACE_TO_OSS_MAP[`__FIRST_MASK_${baseId}__`];
                    if (firstMaskUrl) {
                        finalUrl = firstMaskUrl;
                        console.log('[BizyDraft Upload] 📎 Image upload, using first mask URL');
                    } else {
                        console.log('[BizyDraft Upload] ⏳ Image upload, awaiting mask');
                    }
                }

                // 保存映射
                [filename, `${filename} [input]`, `${filename} [output]`].forEach(key => {
                    window.CLIPSPACE_TO_OSS_MAP[key] = finalUrl;
                });

                const filenameWithoutSuffix = filename.replace(/ \[(input|output)\]$/, '');
                if (filenameWithoutSuffix !== filename) {
                    window.CLIPSPACE_TO_OSS_MAP[filenameWithoutSuffix] = finalUrl;
                }

                console.log('[BizyDraft Upload] 💾 Mapped:', filename, '->', finalUrl);
            }
        }

        // 同时保存后端返回的文件名映射
        window.CLIPSPACE_TO_OSS_MAP[data.name] = finalUrl;

        // 篡改响应，让 ComfyUI 使用完整的 OSS URL
        const modifiedData = { ...data, name: finalUrl, subfolder: '' };
        console.log('[BizyDraft Upload] ✅ Response modified');
        console.log('═══════════════════════════════════════════════════════\n');

        return new Response(JSON.stringify(modifiedData), {
            status: response.status,
            statusText: response.statusText,
            headers: response.headers
        });

    } catch (e) {
        console.error('[BizyDraft Upload] ❌ Error:', e);
        return response;
    }
};

// 转换 prompt 中的 clipspace 路径为 OSS URL
function convertClipspacePathsInPrompt(prompt) {
    if (!prompt || typeof prompt !== 'object') {
        return prompt;
    }

    let conversionsCount = 0;

    for (const [nodeId, node] of Object.entries(prompt)) {
        if (!node?.inputs) continue;

        for (const [inputKey, inputValue] of Object.entries(node.inputs)) {
            if (typeof inputValue === 'string' && inputValue.includes('clipspace')) {
                const match = inputValue.match(/clipspace\/([\w-]+\.(?:png|jpg|jpeg|webp|gif))/i);
                if (match) {
                    const filename = match[1];
                    const ossUrl = findOssUrl(filename);

                    if (ossUrl) {
                        console.log('[BizyDraft Prompt] Converting:', inputValue, '->', ossUrl);
                        node.inputs[inputKey] = ossUrl;

                        if (inputKey === 'image' && node.inputs['image_name']) {
                            node.inputs['image_name'] = ossUrl.split('/').pop();
                        }

                        conversionsCount++;
                    }
                }
            }
        }
    }

    if (conversionsCount > 0) {
        console.log(`[BizyDraft Prompt] Converted ${conversionsCount} path(s)`);
    }

    return prompt;
}

// 注册 ComfyUI 扩展
app.registerExtension({
    name: "bizyair.clipspace.to.oss",

    async setup() {
        const originalGraphToPrompt = app.graphToPrompt;

        app.graphToPrompt = async function(...args) {
            const result = await originalGraphToPrompt.apply(this, args);

            if (result?.output) {
                result.output = convertClipspacePathsInPrompt(result.output);
            }

            return result;
        };

        console.log('[BizyDraft] Extension registered');
    }
});
