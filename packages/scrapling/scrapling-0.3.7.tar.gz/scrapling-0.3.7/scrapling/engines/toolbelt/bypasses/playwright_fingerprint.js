// Remove playwright fingerprint => https://github.com/microsoft/playwright/commit/c9e673c6dca746384338ab6bb0cf63c7e7caa9b2#diff-087773eea292da9db5a3f27de8f1a2940cdb895383ad750c3cd8e01772a35b40R915
delete window.__pwInitScripts;
delete window.__playwright__binding__;