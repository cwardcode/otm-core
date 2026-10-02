"use strict";

function isLoopbackHost(hostname) {
	return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '::1';
}

function normalizeTileHost(settings) {
	if (!settings || !settings.tileHost || !window || !window.location) {
		return settings;
	}

	var tileHost;
	try {
		tileHost = new URL(settings.tileHost, window.location.origin);
	} catch (e) {
		return settings;
	}

	var pageHostIsLoopback = isLoopbackHost(window.location.hostname);
	if (isLoopbackHost(tileHost.hostname) && !pageHostIsLoopback) {
		var normalized = Object.assign({}, settings);
		normalized.tileHost = window.location.origin + '/tiles';
		return normalized;
	}

	return settings;
}

// window.otm is expected to be undefined in our JS test runner
module.exports = window.otm && window.otm.settings
	? Object.freeze(normalizeTileHost(window.otm.settings))
	: {};
