module.exports = {
    env: {
        browser: true,
        es2021: true
    },
    extends: [
        "standard"
    ],
    ignorePatterns: [
        "piweb/3rdparty/*"
    ],
    parserOptions: {
        ecmaVersion: 12,
        sourceType: "module"
    },
    rules: {
        "brace-style": ["error", "stroustrup"],
        "curly": ["off"],
        "indent": ["error", 4],
        "max-len": ["error", { "code": 120 }],
        "no-new-object": ["off"],
        "padded-blocks": ["error", {
            "blocks": "never",
            "classes": "always",
            "switches": "never"
        }],
        "quote-props": ["error", "consistent"],
        "quotes": ["error", "double"],
        "semi": ["error", "always"],
        "space-before-function-paren": ["error", {
            "anonymous": "always",
            "named": "never",
            "asyncArrow": "always"
        }]
    }
};
