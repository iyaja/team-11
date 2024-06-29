export type Result = {
    markdown: string;
    comments: Comment[];
};

export type Comment = {
    quote: {
        start: number;
        end: number;
        text: string;
    };
    comment: string;
    metadata: {
        risk_factor: string;
    };
};
