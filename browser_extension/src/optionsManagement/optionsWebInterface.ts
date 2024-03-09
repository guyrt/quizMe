import { domain } from "../globalSettings";
import { SharedStateReaders } from "../stateTrackers/sharedStateReaders";

export class OptionsWebInterface {
    
    public async signUpAndSaveToken(username : string, password : string) : Promise<string> {
        const url = `${domain}/api/user/create`;

        const formData = new FormData();
        formData.append('email', username);
        formData.append('password', password);

        try {
            const response = await fetch(url, {
                method: "POST",
                body: formData
            });

            if (response.ok && response.status == 200) {
                // save token to storage
                return this.saveToken(response);
            } else {
                return Promise.resolve(response.statusText);
            }
        } catch (error) {
            return Promise.resolve(`${error}`);
        }
    }
    
    public async loginAndSaveToken(username : string, password : string) : Promise<string> {
        const url = `${domain}/api/user/tokens/create`;

        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await fetch(url, {
                method: "POST",
                body: formData
            });

            if (response.ok) {
                return this.saveToken(response);
            } else {
                // return the error.
                return Promise.resolve(response.statusText);
            }
        } catch (error) {
            return Promise.resolve(`${error}`);
        }
        
    }

    public async logoutThisDevice() : Promise<boolean> {
        // drop locally.
        new SharedStateReaders().deleteUserState();

        // delete the token.
        const url = `${domain}/api/user/tokens/delete`;
        return fetch(url, {
            method: "DELETE"
        }).then(() => true);
    }

    private async saveToken(response : Response) : Promise<string> {
        // save the token to storage.
        const j = await response.json();
        const writer = new SharedStateReaders();
        writer.setApiToken(j['key']);
        writer.setUserEmail(j['user']);
        
        // return "ok"
        return Promise.resolve("ok");
    }
}
