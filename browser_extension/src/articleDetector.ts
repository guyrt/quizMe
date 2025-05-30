import { DomClassification } from "./interfaces";

export function classifyPage(url : Location) : DomClassification {

    const classSample = softClassifier(url); 
    console.log("SoftClassifier output: ", classSample);
    return classSample.classification === "unknown" ? hardClassifier(url) : classSample;

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

    if (host == "perplexity.ai" && document.location.href.includes("search")) {
        return "serp";
    }
}

function isArticleByTextContent(): boolean {
    const readingTimeMinutes = document.body.innerText.trim().split(/\s+/).length / 200;
    const linkCount = document.querySelectorAll("a").length;
    const linksPerMinute = linkCount / readingTimeMinutes;
    console.log("Wezo article textclassifier: ", { readingTimeMinutes, linkCount, linksPerMinute });

    return readingTimeMinutes > 4 || (readingTimeMinutes >= 3 && linksPerMinute < 0.8);
}

function softClassifier(url: Location): DomClassification{

    const maybeSerp = getSerps();
    if (maybeSerp != undefined) {
        return {
            classification: "serp",
            reason: "serp"
        }
    }

    const dashCount = url.pathname.match(/\-/g)?.length || 0;
    if (dashCount >= 2) {
        return {
            classification : "article",
            reason : "dashCount"
        };
    }

    const yearRegex = /\/blog\/\d{4}\//; // Regular expression to match /blog/YEAR/ pattern
    if(yearRegex.test(url.pathname) || url.pathname.includes('/news/') || url.pathname.includes('/article/')){
        return {
            classification : "article",
            reason : "urlContent"
        }
    }


    if (isArticleByTextContent()) {
        return {
            classification : "article",
            reason : "textContent"
        }
    }

    const numArticles = document.querySelectorAll('article').length;
    if (numArticles > 0 && numArticles < 3) {
        return {
            classification : "article",
            reason : "hasArticleTag"
        };
    }

    const ids = ['postBody', 'blog-post', 'postContentContainer', 'publicationContent'];
    for (let i = 0; i < ids.length; i++) {
        if (document.getElementById(ids[i])) {
            return {
                classification : "article",
                reason : "id",
                idLookup : ids[i]
            }
        }
    };
    

    const classes = ["single-post" /* substack */, 'blog_categories', 'byline','blog-content' /*huggingface*/];
    for (let i = 0; i < classes.length; i++) {
        if (document.getElementsByClassName(classes[i])) {
            return {
                classification : "article",
                reason : "class",
                idLookup : classes[i]
            }
        }
    };

    // meta tag
    const metaTags = document.getElementsByTagName('meta');

    // Convert the HTMLCollection to an Array and find the desired meta tag
    const metaTag = Array.from(metaTags).find(tag => tag.getAttribute('property') === 'og:type' && tag.getAttribute('content') === 'article');
    if(metaTag){
        return{
            classification:"article",
            reason:"metaTag",   
        }
    }
    
    if(isArticleByProp()){
        return {
            classification:"article",
            reason:"propertyAttribute"
        }
    }
    return {
        classification : "unknown",
        reason : "fallthrough"
    };
    
}

function hardClassifier(url:Location):DomClassification{

    const decision  = randomForestInference(url);
    if (decision){
        return {classification : "article",
                reason: "randomForest"
        }
    }
    // page remains unknown
    return {
        classification : "unknown",
        reason : "fallthrough"
    }
}

function randomForestInference(url:Location):Boolean{
    console.log("In RF inference");
    return false;
}

function isArticleByProp():Boolean{
    const authorProp = document.querySelector('[itemprop="author"]');
    if (authorProp) {
        return true; 
    }

    const dateProp = document.querySelector('[itemprop="datePublished"]');
    if(dateProp){
        return true;
    }

    return false;
}

