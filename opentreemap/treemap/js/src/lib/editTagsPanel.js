// Manage panel for file uploading
"use strict";

var $ = require('jquery'),
    Bacon = require('baconjs'),
    toastr = require('toastr'),
    U = require('treemap/lib/utility.js'),
    _ = require('lodash');

// For modal dialog on jquery
require('bootstrap');


module.exports.init = function(opts) {
    var $panel = '#edit-tags-panel',
    actionStream = new Bacon.Bus(),
    section = 'body',
    addTag = '#add-tag-button',
    $addTagSection = $(addTag),
    deleteTag = '[id^=delete-button]',
    $deleteTagSection = $(deleteTag),
    addTagInput = '#add-tag-input',
    $addTagInputSection = $(addTagInput),
    saveStream = $addTagSection.asEventStream('click'),
    deleteStream = $deleteTagSection.asEventStream('click'),
    tagInputStream = $addTagInputSection.asEventStream('keyup'),
    updateUrl=opts.updateUrl;

    return {
        actionStream: actionStream.map(_.identity),
        saveStream: saveStream,
        deleteStream: deleteStream,
        tagInputStream: tagInputStream
    };
};
