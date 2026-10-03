"use strict";

// This entry module is loaded in 'base.html' and is used to load JS that
// should run on every page on the site

require("../../../../assets/css/sass/main.scss");
require("autotrack");
require("treemap/lib/buttonEnabler.js").run();
require("treemap/lib/export.js").run();

function enforceInstanceBrandingCss() {
    var appCss = document.getElementById('application-css');
    if (!appCss) {
        return;
    }

    var href = appCss.getAttribute('href') || '';
    if (href.indexOf('/main.css') === -1) {
        return;
    }

    // In some webpack modes main.scss is also injected via a <style> tag.
    // That default stylesheet can override the dynamic branded main.css.
    var styles = document.querySelectorAll('style');
    Array.prototype.forEach.call(styles, function(styleEl) {
        var cssText = styleEl.textContent || '';
        var isInjectedMainStylesheet = cssText.indexOf('.wrapper .btn.btn-otmprimary') >= 0 &&
            cssText.indexOf('.management-container .management-sidebar .map-switcher') >= 0;

        if (isInjectedMainStylesheet && styleEl.parentNode) {
            styleEl.parentNode.removeChild(styleEl);
        }
    });

    // Re-append branded CSS to ensure it has the highest cascade priority.
    var brandedLink = appCss.cloneNode(true);
    brandedLink.href = appCss.href;
    if (appCss.parentNode) {
        appCss.parentNode.removeChild(appCss);
    }
    document.head.appendChild(brandedLink);
}

enforceInstanceBrandingCss();

// Polyfill for String.startsWith(), not supported in IE 11
if (!String.prototype.startsWith) {
    String.prototype.startsWith = function (searchString, position) {
        position = position || 0;
        return this.indexOf(searchString, position) === position;
    };
}
