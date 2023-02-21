import React, { useState, useEffect } from "react";
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
  useEffect(() => {
    setLoading(false);
  }, [image]);
  return (
    <>
      {!loading && <LoadingComponent />}
      <img
        className={className}
        src={image}
        alt={alt}
        onLoad={() => setLoading((state) => !state)}
        style={loading ? style : { opacity: 0 }}
      />
    </>
  );
};

export default ImageLoad;
