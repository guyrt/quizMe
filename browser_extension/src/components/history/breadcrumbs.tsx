import React, { useEffect, useState } from "react";
import { Breadcrumb, BreadcrumbResponse, isBasicError } from "../../interfaces";

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
    }, [])

    return (<>
        <h3>Breadcrumbs</h3>

        {loading === true ? 
            <p>loading...</p> : 
            <>
                {breadcrumbs.map((entry, i) => <SingleBreadCrumb key={`bc_${i}`} breadcrumb={entry}/>)}
            </>
        }
        {error === true && <p>Breadcrumbs will be ready in a jiffy.</p>}
    </>) ;

}

const SingleBreadCrumb: React.FC<{key: string, breadcrumb: Breadcrumb}> = ({key, breadcrumb}) => {
    return (<div>
            <a href={breadcrumb.doc_url} target="_blank">{breadcrumb.title ?? breadcrumb.doc_url}</a>
        </div>
    );
}

export default Breadcrumbs;
