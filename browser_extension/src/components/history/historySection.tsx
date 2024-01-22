import React, {useEffect, useState} from "react";
import { VisitHistory } from "../../interfaces";

// Component Props type
type HistorySectionProps = {
    history: VisitHistory
}


const HistorySection: React.FC<HistorySectionProps> = ({ history }) => {

    return (
        <div>
            {history.recent_page_visits.length > 0 && <div>
                <p>Last {history.recent_page_visits.length} visits:</p>
                {history.recent_page_visits.map(x => 
                    <div key='page_{i}'>
                        <a href='#'>{x.date_added}</a>
                    </div>
                )}
            </div>
            }
            {history.recent_domain_visits.length > 0 && <div>
                <p>Last {history.recent_domain_visits.length} pages in this domain:</p>
                {history.recent_domain_visits.map((x, i) => <div key='domain_{i}'>
                    <p>{x.date_added}</p> <a href={x.url} target="_blank">{x.recent_title}</a>
                </div>)}
            </div>}
        </div>
    );
};

export default HistorySection;