import React from "react";
import { RecentDomainVisits, VisitHistory } from "../../interfaces";
import { strFormatDate } from "../../utils/datetime";

// Component Props type
type HistorySectionProps = {
    history: VisitHistory
}


const HistorySection: React.FC<HistorySectionProps> = ({ history }) => {

    return (
        <div>
            <h3>Site Details</h3>
            {history.recent_page_visits.number_visits > 0 && history.recent_page_visits.latest_visit != undefined
                ? <div>
                    <p>You've visited this page {history.recent_page_visits.number_visits} time{history.recent_page_visits.number_visits > 1 ? 's' : ''} before.</p>
                    <p>Last visit {strFormatDate(history.recent_page_visits.latest_visit?.date_added)}</p>
                </div>
                : <div>This is your first time here!</div>}
            {history.recent_domain_visits.length > 0 && <div>

                {history.recent_domain_visits.map((x, i) => <SingleHistorySection idx={i} keyprefix={`history_${i}`} history={x} />)}
            </div>}
        </div>
    );
};

const SingleHistorySection : React.FC<{idx: number, keyprefix: string, history : RecentDomainVisits}> = ({idx, keyprefix, history}) => {

    function formatTitle(urlObj : {recent_title: string, url : string}) {
        if (urlObj.recent_title == undefined || urlObj.recent_title == "") {
            if (urlObj.url.length > 47) {
                return urlObj.recent_title.substring(0, 47) + '...';
            }

            return urlObj.url;
        } else {
            return urlObj.recent_title;
        }
    }

    return (
        <>
        {(idx > 0) && <hr />}
            <div key={keyprefix}>
                {history.title == '__default__' ?
                    <h4>Your history on {history.head}</h4>
                    : <h4>{history.title}</h4>
                }

                {history.urls.slice(0, 8).map((x, i) =>
                    <div className='history-list-item' key={`${keyprefix}_${i}`}>
                        <a href={x.url} target="_blank">{formatTitle(x)}</a>
                        {strFormatDate(x.date_added)}
                    </div>
                )}
            </div>
        </>
    )
}

export default HistorySection;