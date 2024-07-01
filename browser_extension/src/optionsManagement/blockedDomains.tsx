import React, { useEffect, useRef, useState } from "react";
import { SharedStateReaders } from "../stateTrackers/sharedStateReaders";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircleStop, faTrashCan, faCircleCheck, IconDefinition } from "@fortawesome/free-regular-svg-icons";
import { BasicError, ChromeMessage, LooseSetting, isBasicError } from "../interfaces";
import { sendRuntimeMessage } from "../messagePassing/messageProxy";


type DomainListInnerProps = {
    isAllowList : boolean // true iff this is allow list. false iff this is block list.
    domainAddedEvent : "fa_addNewDomainAllow" | "fa_addNewDomainBlock"
    domainRemovedEvent : "fa_deleteDomainBlock" | "fa_deleteDomainAllow"
    headerText: string
    allowListCTA : string
    reminderHint : string
    addIcon : IconDefinition
};

export function BlockedDomainList() {
    return (
        <>
        <DomainListInner 
            isAllowList={false} 
            domainAddedEvent="fa_addNewDomainBlock"
            domainRemovedEvent="fa_deleteDomainBlock"
            headerText="Blocked domains. Pages at these domains will not be stored at all."
            allowListCTA="Block a domain:"
            reminderHint="(This will delete any stored pages on that domain)"
            addIcon={faCircleStop}
        />
        </>
    )
}

export function AllowDomainList() {
    return (
        <>
        <DomainListInner 
            isAllowList={true} 
            domainAddedEvent="fa_addNewDomainAllow"
            domainRemovedEvent="fa_deleteDomainAllow"
            headerText="Allowed domains. Only articles at these domains will be stored."
            allowListCTA="Allow a domain:"
            reminderHint=""
            addIcon={faCircleCheck}
        />
        </>
    )
}

const DomainListInner: React.FC<DomainListInnerProps> = ({ 
    isAllowList, 
    domainAddedEvent,
    domainRemovedEvent,
    headerText,
    allowListCTA,
    reminderHint,
    addIcon
}) => {
    
    const [domains, setDomains] = useState<LooseSetting[]>([]);

    const [errorLoadingDomains, setErrorLoadingDomains] = useState<boolean>(false);

    const [errorAddingDomain, setErrorAddingDomain] = useState<boolean>(false);

    const [addButtonClicked, setAddButtonClicked] = useState<boolean>(false);

    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        resetDomains();
    }, []);

    const removeDomain = (domain : string) => {
        const payload : ChromeMessage = {action: domainRemovedEvent, payload: {domain: domain}};
        sendRuntimeMessage(payload, (response) => {
            resetDomains();
        });
    }
    
    const addDomainToList = async () => {
        setAddButtonClicked(true);
        setTimeout(() => setAddButtonClicked(false), 100); // Resets the click state after 200ms
        
        const value = inputRef.current?.value;
        if (value == undefined || value == "") {
            return;
        }

        if (domains.findIndex((x) => x.value === value) > -1) {
            return;
        }

        const payload = {action: domainAddedEvent, payload: {domain: value}};
        sendRuntimeMessage(payload, 
            function(response) {
                if (response.success) {
                    resetDomains();
                    setErrorAddingDomain(false);
                } else {
                    setErrorAddingDomain(true);
                }
            }
        );
    }

    function resetDomains() {
        (new SharedStateReaders()).getDomainList(true, !isAllowList).then((domains : LooseSetting[] | BasicError) => {
            if (isBasicError(domains)) {
                setErrorLoadingDomains(true);
            } else {
                setErrorLoadingDomains(false);
                setDomains(domains || []);
            }
        })
    }

    function inputKeyPress(event : React.KeyboardEvent) {
        if (event.key === 'Enter') {
            addDomainToList();
            return true;
        }
        return false;
    }

    return (
        <div className="listOfDomains">
            <p>{ headerText }</p>
            {errorLoadingDomains && <p>uh oh... trouble loading domains.</p>}
            {domains.map((d, i) => 
                <SingleDomain 
                    domain={d.value} 
                    removeDomain={removeDomain}
                    key={`domainList_${i}`}
                    />
            )}
            <div className='addDomainSpan'>
                <span className="right-pad">{allowListCTA}</span>
                {errorAddingDomain && <p>uh oh... troubling adding a domain. Try again in a little while.</p>}
                <input type="text" ref={inputRef} onKeyDown={inputKeyPress}></input>
                <span 
                    className={`addDomainButton option-icon-clickable ${addButtonClicked ? 'option-icon-clicked' : ''}`}
                    onClick={addDomainToList}>
                    <FontAwesomeIcon icon={addIcon} />
                </span>
                <p>{reminderHint}</p>
            </div>
        </div>
    );
}

// todo rename.
type SingleDomainProps = {
    domain: string;
    removeDomain : (x : string) => void
};

const SingleDomain: React.FC<SingleDomainProps> = ({ domain, removeDomain }) => {

    const [isClicked, setIsClicked] = useState(false);

    function clickHandle() {
        setIsClicked(true);
        setTimeout(() => {
            setIsClicked(false)
        }, 100);
        removeDomain(domain);    
    }

    return (
        <div className="singleDomainWrapper" onClick={clickHandle}>
            <span className={`option-trashcan option-icon-clickable ${isClicked ? 'option-icon-clicked' : ''}`}>
                <FontAwesomeIcon icon={faTrashCan} />
            </span> 
            <span>{domain}</span>
        </div>
    )
}
