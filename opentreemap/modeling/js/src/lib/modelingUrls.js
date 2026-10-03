'use strict';

var _ = require('lodash'),
    F = require('modeling/lib/func.js'),
    config = require('treemap/lib/config.js');

function ModelingUrls(urls) {
    var instanceUrl = config.instance.url;

    // Create getter methods for each url.
    var result = _.mapValues(urls, F.getter);

    // Override getter methods for urls that require parameters.
    result = _.extend(result, {
        planUrl: function(planId) {
            return joinPath(instanceUrl, 'modeling/plans/' + planId + '/');
        }
    });

    return result;
}

function joinPath(base, suffix) {
    var normalizedBase = (base || '').replace(/\/?$/, '/'),
        normalizedSuffix = (suffix || '').replace(/^\//, '');

    return normalizedBase + normalizedSuffix;
}

module.exports = ModelingUrls;
