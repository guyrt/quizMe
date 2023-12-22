
export type DomClassification = {
    classification : "article" | "unknown",
    reason : "hasArticleTag" | "dashCount" | "textContent" | "postBody" | "blog-post" | "fallthrough"
}

export function isArticle(url : Location) : DomClassification {
    if (document.querySelector('article') !== null) {
        return {
            classification : "article",
            reason : "hasArticleTag"
        };
    }

    if (document.getElementById('postBody')) {
        return {
            classification : "article",
            reason : "postBody"
        }
    }

    if (document.getElementById('blog-post')) {
        return {
            classification : "article",
            reason : "blog-post"
        }
    }

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