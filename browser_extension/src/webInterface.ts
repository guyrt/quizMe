import {
  UploadedDom,
  UploadableDomShape,
  QuizResponse,
  Quiz,
  QuizHistory,
} from './interfaces'
import { sharedState } from './stateTrackers/sharedState'
import { domain } from './globalSettings'

export async function uploadQuizResults(
  payload: QuizResponse,
): Promise<undefined> {
  const url = `${domain}/api/quiz/uploadresults`
  const token = (await sharedState.getApiToken()) ?? 'todo'
  return post(token, url, payload)
}

export async function sendDomPayload(
  token: string,
  payload: UploadableDomShape,
): Promise<UploadedDom> {
  console.log('sendDomPayload')
  const url = `${domain}/api/browser/writehtml`

  return post(token, url, payload) // TODO - this could return undefined.
}

export async function sendDomPayloadUpdate(
  token: string,
  payload: UploadableDomShape,
): Promise<UploadedDom> {
  console.log('sendDomPayload')
  const url = `${domain}/api/browser/rewritehtml`

  return post(token, url, payload) // TODO - this could return undefined.
}

/// Request a quiz
export async function getAQuiz(
  payload: UploadedDom,
  forceReload: boolean,
): Promise<UploadedDom> {
  const url = `${domain}/api/quiz/makequiz`
  const apiToken = await sharedState.getApiToken()
  if (apiToken == undefined) {
    return { ...payload, quiz_context: { previous_quiz: { status: 'error' } } }
  }

  const fullPayload = { ...payload, force_recreate: forceReload }

  return post(apiToken, url, fullPayload)
    .then((q: any) => {
      // note: overwrites only quizzes. This is critical to avoid
      // clobbering other parts of a dom payload.
      if (q) {
        return { ...payload, quiz_context: (q as UploadedDom).quiz_context }
      } else {
        return {
          ...payload,
          quiz_context: { previous_quiz: createErrorQuiz() },
        }
      }
    })
    .catch(error => {
      console.error('Error calling API: ', error)
      return { ...payload, quiz_context: { previous_quiz: createErrorQuiz() } }
    })
}

export async function getQuizHistory(): Promise<QuizHistory | undefined> {
  const url = `${domain}/api/quiz/stats`
  const apiToken = await sharedState.getApiToken()
  if (apiToken == undefined) {
    return undefined
  }

  return get(apiToken, url)
    .then(x => {
      if (x != undefined) {
        return x as QuizHistory
      } else {
        return undefined
      }
    })
    .catch(error => {
      console.error('Error calling QuizHistory: ', error)
      return undefined
    })
}

function createErrorQuiz(): Quiz {
  return {
    status: 'error',
    content: [],
    id: 'error',
    owner: 'error',
    reasoning: 'error',
  }
}

// Todo - eventually may need a payload... or combine with post...
function get<OutT>(token: string, url: string): Promise<OutT> {
  const headers = {
    'X-API-KEY': token,
    'Content-Type': 'application/json',
  }

  const p = fetch(url, {
    method: 'GET',
    headers: headers,
  }).then(response => {
    if (response.ok) {
      return response.json()
    }
    throw new Error(`HTTP error! status: ${response.status}`)
  })

  return p
}

function post<InT, OutT>(
  token: string,
  url: string,
  payload: InT,
): Promise<OutT> {
  console.log(`Posting to ${url}`)

  const headers = {
    'X-API-KEY': token,
    'Content-Type': 'application/json',
  }

  const p = fetch(url, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify(payload),
  }).then(response => {
    if (response.ok) {
      return response.json()
    }
    throw new Error(`HTTP error! status: ${response.status}`)
  })

  return p
}
