import { Readability } from "@mozilla/readability";

function getReaderMode(dom : Document) {
    const copy = dom.cloneNode(true);
    const r = new Readability(copy as Document).parse();
    return r;
}

export default getReaderMode;