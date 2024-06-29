export type Result = {
    markdown: string;
    comments: Comment[];
    features: Array<{
        name: string;
        score: number;
    }>;
    summary: string;
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
