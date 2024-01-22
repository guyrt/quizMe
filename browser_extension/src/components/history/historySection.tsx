import React from "react";
import { VisitHistory } from "../../interfaces";
import { strFormatDate } from "../../utils/datetime";

// Component Props type
type HistorySectionProps = {
    history: VisitHistory
}


const HistorySection: React.FC<HistorySectionProps> = ({ history }) => {

    return (
        <div>
            {history.recent_page_visits.length > 0 && <div>
                <p>Last {history.recent_page_visits.length} visits:</p>
                {history.recent_page_visits.map((x, i) => 
                    <div key={`page_${i}`}>
                        <a href='#'>{strFormatDate(x.date_added)}</a>
                    </div>
                )}
            </div>
            }
            {history.recent_domain_visits.length > 0 && <div>
                <p>Last {history.recent_domain_visits.length} pages in this domain:</p>
                {history.recent_domain_visits.map((x, i) => <div key={`domain_${i}`}>
                    <p>{strFormatDate(x.date_added)}</p> <a href={x.url} target="_blank">{x.recent_title}</a>
                </div>)}
            </div>}
        </div>
    );
};

export default HistorySection;