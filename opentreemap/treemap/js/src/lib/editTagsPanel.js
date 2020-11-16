// Manage panel for file uploading
"use strict";

var $ = require('jquery'),
    Bacon = require('baconjs'),
    toastr = require('toastr'),
    U = require('treemap/lib/utility.js'),
    _ = require('lodash');

// For modal dialog on jquery
require('bootstrap')


module.exports.init = function(opts) {
    var $panel = '#edit-tags-panel',
    actionStream = new Bacon.Bus(),
    section = 'body',
    addTag = '#add-tag-button',
    $addTagSection = $(addTag),
    deleteTag = '#delete-tag-button',
    $deleteTagSection = $(deleteTag),
    addTagInput = '#add-tag-input',
    $addTagInputSection = $(addTagInput),
    deleteTags = function(opts) { console.log('opts are: ', opts)},
    saveStream = $addTagSection.asEventStream('click'),
    deleteStream = $deleteTagSection.asEventStream('click').doAction(deleteTags, true),
    tagInputStream = $addTagInputSection.asEventStream('keyup'),
    updateUrl=opts.updateUrl;

    // console.log($addTagSection);
    // console.log($deleteTagSection);
    // console.log($addTagInputSection);

    // actionStream.plug(deleteStream);
    // actionStream.plug(saveStream);
    // actionStream.plug(tagInputStream);

    tagInputStream.onValue((event) => {
        console.log('val is', event.target.value)
    })

    saveStream.onValue((event) => {
        if($addTagInputSection.val()) {
            console.log(`adding ${$addTagInputSection.val()}`);
            var data = $addTagInputSection.val();

            return Bacon.fromPromise($.ajax({
                url: updateUrl,
                type: 'PUT',
                contentType: "application/json",
                data: JSON.stringify(data)
            }));
        }
    })

    deleteStream.onValue((event) => {
        console.log('delete button was clicked', event);
    })

    return {
        actionStream: actionStream.map(_.identity),
        saveStream,
        deleteStream,
        tagInputStream
    };
};
