/**
 * TechGap Logo Component
 */
import logoPng from '../../assets/logo.png';

const TechGapLogo = ({ className = "w-8 h-8" }) => (
    <img src={logoPng} alt="TechGap Logo" className={`${className} object-contain`} />
);

export default TechGapLogo;
