import React, { useEffect, useState } from "react";
import { Breadcrumb, BreadcrumbResponse, isBasicError } from "../../interfaces";
import { strFormatDate } from "../../utils/datetime";

export type BreadcrumbsProps = {
    activePage : string
}

const Breadcrumbs: React.FC<BreadcrumbsProps> = ({activePage}) => {

    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState(false);

    const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbResponse>([]);

    useEffect(() => {
        chrome.runtime.sendMessage({action: "fa_getbreadcrumbs", payload: {pageId: activePage}}, (breadcrumbs) => {
            setLoading(false);

            if (isBasicError(breadcrumbs)) {
                setError(true);
            } else {
                setError(false);
                setBreadcrumbs(breadcrumbs);
            }

        })
    }, [activePage])

    return (<>
        <h3>Breadcrumbs</h3>

        {loading === true ? 
            <p>loading...</p> : 
            <>
                {breadcrumbs.map((entry, i) => <SingleBreadCrumb idx={`bc_${i}`} breadcrumb={entry}/>)}
            </>
        }
        {error === true && <p>Breadcrumbs will be ready in a jiffy.</p>}
    </>) ;

}

const SingleBreadCrumb: React.FC<{idx: string, breadcrumb: Breadcrumb}> = ({idx, breadcrumb}) => {
    
    function chooseLink() {
        if (breadcrumb.title == undefined || breadcrumb.title == "") {
            return breadcrumb.doc_url;
        } else {
            return breadcrumb.title;
        }
    }
    
    return (<div className="history-list-item" key={idx}>
            <a href={breadcrumb.doc_url} target="_blank">{breadcrumb.title ?? breadcrumb.doc_url}</a>
            {breadcrumb.last_modified != undefined && strFormatDate(breadcrumb.last_modified)}
        </div>
    );
}

export default Breadcrumbs;
