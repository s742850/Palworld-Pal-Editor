// Public build settings only. No wallet secrets belong in a frontend bundle.
export function parseSupportConfig(env = {}) {
    const value = env.VITE_SUPPORT_URL?.trim();
    const address = env.VITE_SUPPORT_ADDRESS?.trim() || '';
    const network = env.VITE_SUPPORT_NETWORK?.trim() || '';
    const asset = env.VITE_SUPPORT_ASSET?.trim() || '';
    if (!value && !address) return null;
    try {
        const url = value ? new URL(value) : null;
        if (url && (url.protocol !== 'https:' || url.username || url.password)) return null;
        // Format check only; network ownership must be verified by the maintainer.
        if (address && (!/^[a-zA-Z0-9:_-]{10,200}$/.test(address) || !network || !asset)) return null;
        return {
            url: url?.href || null,
            address,
            asset,
            name: env.VITE_SUPPORT_NAME?.trim() || 'Fork maintainer',
            network,
        };
    } catch {
        return null;
    }
}

export const supportConfig = parseSupportConfig(import.meta.env);
