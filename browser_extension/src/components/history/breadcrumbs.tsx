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

            }

        })
    }, [])

    return (<>
        Breadcrumbs

        {loading === true ? 
            <p>loading...</p> : 
            <>
                {breadcrumbs.map((entry, i) => <SingleBreadCrumb key={`bc_${i}`} breadcrumb={entry}/>)}
            </>}
        {error === true && <p>Breadcrumbs will be back in a jiffy.</p>}
    </>) ;

}

const SingleBreadCrumb: React.FC<{key: string, breadcrumb: Breadcrumb}> = ({key, breadcrumb}) => {
    return (<div>
            <a href={breadcrumb.doc_url}>{breadcrumb.doc_url}</a>
        </div>
    );
}

export default Breadcrumbs;
