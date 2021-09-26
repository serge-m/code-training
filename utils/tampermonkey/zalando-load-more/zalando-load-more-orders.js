// ==UserScript==
// @name         zalando-load-more-button
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Automatically press "load more" button in the list of orders.
// @author       serge-m
// @match        https://*.zalando.de/*
// @icon         data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    var theTimeout = null;

    function randn_bm() {
        var u = 0, v = 0;
        while (u === 0) u = Math.random();
        while (v === 0) v = Math.random();
        return Math.sqrt( -2.0 * Math.log( u ) ) * Math.cos( 2.0 * Math.PI * v );
    }

    function recursiveExpandLoadMore() {
        if(theTimeout) {
            clearTimeout(theTimeout);
        }

        var button = null;
        for (const a of document.querySelectorAll("button")) {
            if (a.textContent.includes("Load more")) {
                button = a;
                break;
            }
        }

        var nextTime = 1000;
        if(button) {
            console.log("found button. loading");
            button.click();
            nextTime = 765 + 300 * randn_bm();
            nextTime = Math.max(234, nextTime);
            console.log("next time " + nextTime);
        }

        theTimeout = setTimeout(recursiveExpandLoadMore, nextTime);
    }

    recursiveExpandLoadMore();

})();
