import React, { useState, useEffect } from "react";

interface Fetch<T> {
  uri: string;
  renderSuccess: ({ data }: { data: T }) => JSX.Element;
  loadingFallback: () => JSX.Element;
  renderError?: () => JSX.Element;
}
interface State<T> {
  loading: boolean;
  data?: T;
  error?: Error;
}
export function useFetch<T>(uri: string): State<T> {
  const [data, setData] = useState();
  const [error, setError] = useState();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!uri) return;
    fetch(uri)
      .then((data) => data.json())
      .then(setData)
      .then(() => setLoading(false))
      .catch(setError);
  }, [uri]);

  return {
    loading,
    data,
    error,
  };
}

export default function Fetch<T>({
  uri,
  renderSuccess,
  loadingFallback,
  renderError = () => <pre>Error</pre>,
}: Fetch<T>) {
  const { loading, data, error } = useFetch<T>(uri);
  if (loading) return loadingFallback();
  if (error) return renderError();
  if (data) return renderSuccess({ data });
  return <></>;
}
