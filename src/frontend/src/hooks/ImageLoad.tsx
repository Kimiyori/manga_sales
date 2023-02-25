import React, { useState, useEffect, useRef } from "react";
import LoadingComponent from "../components/core/LoadingComponent/loadingComponent";

type ImageType = {
  className?: string;
  src: string;
  alt: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  style?: any;
};

const ImageLoad: React.FunctionComponent<ImageType> = ({ className, src, alt, style }) => {
  const [loading, setLoading] = useState(false);
  const [image] = useState(src);
  const imgRef = useRef<HTMLImageElement>(null);
  useEffect(() => {
    if (loading) setLoading(true);
  }, [loading]);
  useEffect(() => {
    if (imgRef.current) imgRef.current.style.opacity = "100";
  }, [image]);
  return (
    <>
      {!loading && <LoadingComponent />}
      <img
        ref={imgRef}
        className={className}
        src={image}
        alt={alt}
        onLoad={() => setLoading((state) => !state)}
        style={{ opacity: 0, ...style }}
      />
    </>
  );
};

export default ImageLoad;
