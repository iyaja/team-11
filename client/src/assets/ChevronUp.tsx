import React from "react";

export default React.memo(function ChevronUp({
    color = 'currentColor',
}: {
    color?: string;
}) {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="m8 5 4 6H4l4-6Z" fill={color}/>
            </svg>
        );
});
