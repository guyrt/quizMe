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
            <h3>Details</h3>
            {history.recent_page_visits.number_visits > 0 && history.recent_page_visits.latest_visit != undefined
                ? <div>
                    <p>You've visited this page {history.recent_page_visits.number_visits} time{history.recent_page_visits.number_visits > 1 ? 's' : ''} before.</p>
                    <p>Last visit {strFormatDate(history.recent_page_visits.latest_visit?.date_added)}</p>
                </div> 
                : <div>This is your first time here!</div>}
            {history.recent_domain_visits.length > 0 && <div>
                <p>Last {history.recent_domain_visits.length} pages in this domain:</p>
                {history.recent_domain_visits.map((x, i) => 
                    <div className='history-list-item' key={`domain_${i}`}>
                        <a href={x.url} target="_blank">{x.recent_title}</a>
                        {strFormatDate(x.date_added)}
                    </div>
                )}
            </div>}
        </div>
    );
};

export default HistorySection;