
export type DomClassification = {
    classification : "article" | "unknown",
    reason : "hasArticleTag" | "dashCount" | "textContent" | "id" | "class" | "fallthrough",
    
    // these are specific lookups that are likely candidates.
    idLookup? : string,
    classlookup? : string
}

export function classifyPage(url : Location) : DomClassification {
    if (document.querySelector('article') !== null) {
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

    // fallback to no
    return {
        classification : "unknown",
        reason : "fallthrough"
    }
}

function isArticleByTextContent(): boolean {
    const readingTimeMinutes = document.body.innerText.trim().split(/\s+/).length / 200;
    const linkCount = document.querySelectorAll("a").length;
    const linksPerMinute = linkCount / readingTimeMinutes;
    // console.log({ readingTimeMinutes, linkCount, linksPerMinute });

    return readingTimeMinutes >= 3 && linksPerMinute < 0.8;
}