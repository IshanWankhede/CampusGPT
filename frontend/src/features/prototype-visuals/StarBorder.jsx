import React from 'react';

const StarBorder = ({
  as: Component = 'div',
  className = '',
  color = 'white',
  speed = '5s',
  thickness = 1,
  backgroundColor = '#141416',
  textColor = '#ffffff',
  borderColor = 'rgba(255, 255, 255, 0.1)',
  innerClassName = '',
  focusOnly = true,
  children,
  ...rest
}) => {
  return (
    <Component
      className={`relative inline-block overflow-hidden rounded-[14px] ${focusOnly ? 'star-border-container' : ''} ${className}`}
      style={{
        padding: `${thickness}px`,
        ...rest.style
      }}
      {...rest}
    >
      <div
        className={`absolute w-[300%] h-[50%] bottom-[-11px] right-[-250%] rounded-full animate-star-movement-bottom z-0 pointer-events-none ${
          focusOnly ? 'star-movement-glow' : 'opacity-70'
        }`}
        style={{
          background: `radial-gradient(circle, ${color}, transparent 10%)`,
          animationDuration: speed
        }}
      ></div>
      <div
        className={`absolute w-[300%] h-[50%] top-[-10px] left-[-250%] rounded-full animate-star-movement-top z-0 pointer-events-none ${
          focusOnly ? 'star-movement-glow' : 'opacity-70'
        }`}
        style={{
          background: `radial-gradient(circle, ${color}, transparent 10%)`,
          animationDuration: speed
        }}
      ></div>
      <div
        className={`relative z-1 border rounded-[13px] star-border-inner ${innerClassName}`}
        style={{ background: backgroundColor, color: textColor, borderColor }}
      >
        {children}
      </div>
    </Component>
  );
};

export default StarBorder;
