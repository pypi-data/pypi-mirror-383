import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

window.CLIPSPACE_TO_OSS_MAP = window.CLIPSPACE_TO_OSS_MAP || {};


const originalFetchApi = api.fetchApi;
api.fetchApi = async function(url, options) {
    const response = await originalFetchApi.call(this, url, options);
    console.log(url,'url--------------------');
    if ((url==='/upload/image' || url==='/upload/mask') && response.ok) {
        try {
            const clonedResponse = response.clone();
            const data = await clonedResponse.json();

            if (data && data.name && data.subfolder) {
                if (options && options.body && options.body instanceof FormData) {
                    const imageFile = options.body.get('image');
                    if (imageFile && imageFile.name) {
                        const originalFilename = imageFile.name;

                        let ossUrl;
                        if (data.name.startsWith('http://') || data.name.startsWith('https://')) {
                            ossUrl = data.name;
                        } else if (data.subfolder && (data.subfolder.includes('http://') || data.subfolder.includes('https://'))) {
                            ossUrl = `${data.subfolder}/${data.name}`;
                        } else {
                            return response;
                        }

                        window.CLIPSPACE_TO_OSS_MAP[originalFilename] = ossUrl;

                        const filenameWithoutSuffix = originalFilename.replace(/ \[(input|output)\]$/, '');
                        if (filenameWithoutSuffix !== originalFilename) {
                            window.CLIPSPACE_TO_OSS_MAP[filenameWithoutSuffix] = ossUrl;
                        }
                    }
                }
            }
        } catch (e) {
            console.warn('[BizyDraft ClipspaceToOss] Failed to parse upload response:', e);
        }
    }

    return response;
};

/**
 * Convert clipspace paths to OSS URLs in a prompt object
 * @param {Object} prompt - The prompt object to process
 * @returns {Object} The processed prompt object
 */
function convertClipspacePathsInPrompt(prompt) {
    if (!prompt || typeof prompt !== 'object') {
        return prompt;
    }

    let conversionsCount = 0;

    // Iterate through all nodes in the prompt
    for (const [nodeId, node] of Object.entries(prompt)) {
        if (!node || !node.inputs) {
            continue;
        }

        // Check all input values
        for (const [inputKey, inputValue] of Object.entries(node.inputs)) {
            if (typeof inputValue === 'string' && inputValue.includes('clipspace')) {
                // Extract the filename from paths like:
                // "clipspace/clipspace-mask-12345.png [input]"
                // "clipspace/clipspace-painted-masked-12345.png [input]"
                const match = inputValue.match(/clipspace\/([\w-]+\.(?:png|jpg|jpeg|webp|gif))/i);
                if (match) {
                    const filename = match[1]; // e.g., "clipspace-mask-12345.png"

                    // Look for this filename in our mapping (with or without [input]/[output] suffix)
                    const filenameWithInput = `${filename} [input]`;
                    const filenameWithOutput = `${filename} [output]`;

                    let ossUrl = window.CLIPSPACE_TO_OSS_MAP[filename]
                              || window.CLIPSPACE_TO_OSS_MAP[filenameWithInput]
                              || window.CLIPSPACE_TO_OSS_MAP[filenameWithOutput];

                    if (ossUrl) {
                        console.log(`[BizyDraft ClipspaceToOss] Converting: ${inputValue} -> ${ossUrl}`);
                        node.inputs[inputKey] = ossUrl;

                        // Also update image_name if it exists
                        if (inputKey === 'image' && node.inputs['image_name']) {
                            // Extract just the filename from the OSS URL
                            const ossFilename = ossUrl.split('/').pop();
                            node.inputs['image_name'] = ossFilename;
                            console.log(`[BizyDraft ClipspaceToOss] Also updated image_name to: ${ossFilename}`);
                        }

                        conversionsCount++;
                    } else {
                        console.warn(`[BizyDraft ClipspaceToOss] No OSS URL found for clipspace file: ${filename}`);
                        console.warn('[BizyDraft ClipspaceToOss] Available mappings:', Object.keys(window.CLIPSPACE_TO_OSS_MAP));
                    }
                }
            }
        }
    }

    if (conversionsCount > 0) {
        console.log(`[BizyDraft ClipspaceToOss] Converted ${conversionsCount} clipspace path(s) to OSS URLs`);
    }

    return prompt;
}

app.registerExtension({
    name: "bizyair.clipspace.to.oss",

    async setup() {
        const originalGraphToPrompt = app.graphToPrompt;

        app.graphToPrompt = async function(...args) {
            console.log('[BizyDraft ClipspaceToOss] graphToPrompt called, intercepting...');

            const result = await originalGraphToPrompt.apply(this, args);

            if (result && result.output) {
                result.output = convertClipspacePathsInPrompt(result.output);
            }

            return result;
        };
    }
});
