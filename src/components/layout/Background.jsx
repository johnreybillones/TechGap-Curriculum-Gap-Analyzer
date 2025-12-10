/**
 * Background Component
 * Fixed background with gradient and grid pattern
 */
const Background = () => {
    return (
        <>
            <div className="fixed inset-0 -z-10 h-full w-full bg-[radial-gradient(#cbd5e1_1px,transparent_1px)] dark:bg-[radial-gradient(#334155_1px,transparent_1px)] [background-size:24px_24px] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_70%,transparent_100%)] opacity-100 dark:opacity-20"></div>
            <div className="fixed inset-0 -z-20 h-full w-full bg-slate-50 dark:bg-slate-900 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-100/50 via-slate-50 to-slate-50 dark:from-slate-800/50 dark:via-slate-900 dark:to-slate-900 transition-colors duration-300"></div>
        </>
    );
};

export default Background;
