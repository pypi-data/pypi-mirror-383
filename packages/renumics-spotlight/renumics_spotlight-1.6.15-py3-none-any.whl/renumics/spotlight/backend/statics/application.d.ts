interface Edition {
    name: string;
    shorthand: string;
}
interface Application {
    edition: Edition;
    version: string;
    apiUrl?: string;
    publicUrl?: string;
    docsUrl: string;
    repositoryUrl: string;
    filebrowsingAllowed: boolean;
}
declare const application: Application;
export default application;
