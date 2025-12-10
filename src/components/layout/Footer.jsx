/**
 * Footer Component
 */
const Footer = () => {
    return (
        <footer className="py-4 text-center text-slate-400 dark:text-slate-600 text-xs md:text-sm relative z-0">
            <p>&copy; {new Date().getFullYear()} Evalrey. All rights reserved.</p>
        </footer>
    );
};

export default Footer;
