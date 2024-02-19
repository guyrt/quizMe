import { Readability } from "@mozilla/readability";


export function getCleanDom(dom : Document) : Document {
    const domCopy : Document = dom.cloneNode(true) as Document;
    const embeddedImages = domCopy.querySelectorAll('img[src^="data:image"]');
    embeddedImages.forEach(x => x.remove());

    const svgs = domCopy.querySelectorAll('svg');
    svgs.forEach(x => x.remove());

    domCopy.querySelectorAll('script').forEach(x => x.remove());
    domCopy.querySelectorAll('style').forEach(x => x.remove());

    return domCopy;
}


export function getReaderMode(dom : Document) {
    const copy = getCleanDom(dom);
    const r = new Readability(copy as Document).parse();
    return r;
}
