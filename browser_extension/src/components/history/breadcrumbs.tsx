import React, { useEffect, useState } from "react";

export type BreadcrumbsProps = {
    activePage : string
}

const Breadcrumbs: React.FC<BreadcrumbsProps> = ({activePage}) => {

    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        chrome.runtime.sendMessage({action: "fa_getbreadcrumbs", payload: {pageId: activePage}}, (breadcrumbs) => {
            setLoading(false);
        })
    }, [])

    return (<>
        Breadcrumbs

        {loading === true ? <p>loading...</p> : <></>}
    </>) ;

}

export default Breadcrumbs;
