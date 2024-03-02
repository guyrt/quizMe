import React, { useEffect, useRef, useState } from "react";
import { SharedStateReaders } from "../stateTrackers/sharedStateReaders";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircleStop, faTrashCan } from "@fortawesome/free-regular-svg-icons";
import { BasicError, LooseSetting } from "../interfaces";


export function BlockedDomains() {
    
    const [domains, setDomains] = useState<LooseSetting[]>([]);

    const [errorLoadingDomains, setErrorLoadingDomains] = useState<boolean>(false);

    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        resetDomains();
    }, []);

    const removeDomainBlock = (domain : string) => {
        const payload = {action: "fa_deleteDomainBlock", payload: {domain: domain}};
        chrome.runtime.sendMessage(payload, (response) => {
            resetDomains();
        });
    }
    
    const addDomainBlock = async () => {
        const value = inputRef.current?.value;
        if (value == undefined || value == "") {
            return;
        }

        if (domains.findIndex((x) => x.value === value) > -1) {
            return;
        }

        const payload = {action: "fa_addNewDomainBlock", payload: {domain: value}};
        chrome.runtime.sendMessage(payload, 
            function(response) {
                resetDomains();
            }
        );
    }

    function resetDomains() {
        (new SharedStateReaders()).getDomainBlockList(true).then((domains : LooseSetting[] | BasicError) => {
            if ('error' in domains) {
                setErrorLoadingDomains(true);
            } else {
                setErrorLoadingDomains(false);
                setDomains(domains || []);
            }
        })
    }

    return (
        <div className="blockedDomains">
            <p>Blocked domains. Every page at these domains will not be stored at all.</p>
            {errorLoadingDomains && <p>uh oh... trouble loading domains.</p>}
            {domains.map((d, i) => 
                <BlockedDomain 
                    domain={d.value} 
                    removeDomain={removeDomainBlock}
                    key={`blockedDomain_${i}`}
                    />
            )}
            <div className='addDomainBlockSpan'>
                <span className="right-pad">Block a domain:</span>
                <input type="text" ref={inputRef}></input>
                <span className='addDomainBlockButton' onClick={addDomainBlock}><FontAwesomeIcon icon={faCircleStop} /></span>
                <p>(This will delete any stored pages on that domain)</p>
            </div>
        </div>
    );
}


type BlockedDomainProps = {
    domain: string;
    removeDomain : (x : string) => void
};

const BlockedDomain: React.FC<BlockedDomainProps> = ({ domain, removeDomain }) => {

    const [isRemoving, setIsRemoving] = useState(false);

    function clickHandle() {
        removeDomain(domain);
    }

    return (
        <div className="blockedDomainWrapper" onClick={clickHandle}>
            <span className="option-trashcan"><FontAwesomeIcon icon={faTrashCan} /></span> <span>{domain}</span>
        </div>
    )
}
