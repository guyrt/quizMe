import { DomClassification } from "./interfaces";

export function classifyPage(url : Location) : DomClassification {

    // some pages have many articles - these are typically homepages like stratechery.com or espn.com/mlb
    const numArticles = document.querySelectorAll('article').length;
    if (numArticles > 0 && numArticles < 3) {
        return {
            classification : "article",
            reason : "hasArticleTag"
        };
    }

    const ids = ['postBody', 'blog-post'];
    for (let i = 0; i < ids.length; i++) {
        if (document.getElementById(ids[i])) {
            return {
                classification : "article",
                reason : "id",
                idLookup : ids[i]
            }
        }
    };
    

    const classes = ['blog-content' /*huggingface*/, "single-post" /* substack */,];
    for (let i = 0; i < classes.length; i++) {
        if (document.getElementById(classes[i])) {
            return {
                classification : "article",
                reason : "class",
                idLookup : classes[i]
            }
        }
    };

    // many times articles have title with dashes.
    const dashCount = url.pathname.match(/\-/g)?.length || 0;
    if (dashCount >= 2) {
        return {
            classification : "article",
            reason : "dashCount"
        };
    }

    if (isArticleByTextContent()) {
        return {
            classification : "article",
            reason : "textContent"
        }
    }

    const maybeSerp = getSerps();
    if (maybeSerp != undefined) {
        return {
            classification: "serp",
            reason: "serp"
        }
    } 

    // fallback to no
    return {
        classification : "unknown",
        reason : "fallthrough"
    }
}


function getSerps() : string | undefined {
    const host = document.location.host;
    const path = document.location.pathname;

    if (host == "www.bing.com" && path == "/search") {
        return "serp";
    }

    if (host == "www.google.com" && path == "/search") {
        return "serp";
    }

    if (host == "duckduckgo.com" && document.location.href.includes("&q=")) {
        return "serp";
    }
}


function isArticleByTextContent(): boolean {
    const readingTimeMinutes = document.body.innerText.trim().split(/\s+/).length / 200;
    const linkCount = document.querySelectorAll("a").length;
    const linksPerMinute = linkCount / readingTimeMinutes;
    // console.log({ readingTimeMinutes, linkCount, linksPerMinute });

    return readingTimeMinutes > 4 || (readingTimeMinutes >= 3 && linksPerMinute < 0.8);
}