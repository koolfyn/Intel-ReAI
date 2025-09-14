module.exports = {
    webpack: function (config, env) {
      return config;
    },
    devServer: function (configFunction) {
      return function (proxy, allowedHost) {
        const config = configFunction(proxy, allowedHost);
  
        // Force override the invalid value
        config.allowedHosts = "all";
  
        return config;
      };
    },
  };
  