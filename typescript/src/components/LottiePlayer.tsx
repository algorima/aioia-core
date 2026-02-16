"use client";

import { useEffect, useState, ComponentType } from "react";
import type { CSSProperties } from "react";

export interface LottiePlayerProps {
  src: string;
  className?: string;
  loop?: boolean;
  autoplay?: boolean;
  style?: CSSProperties;
  speed?: number;
  keepLastFrame?: boolean;
}

/**
 * Lottie 애니메이션을 렌더링하는 재사용 가능한 컴포넌트입니다.
 * useEffect를 사용하여 클라이언트 사이드에서만 렌더링됩니다.
 *
 * @param props 컴포넌트 props
 * @param props.src Lottie JSON 파일의 경로 또는 URL
 * @param [props.className] 컴포넌트에 적용할 추가 클래스 이름
 * @param [props.loop=true] 애니메이션 반복 여부
 * @param [props.autoplay] 자동 재생 여부. Chromatic 환경이 아닐 경우 기본값은 `true`입니다.
 * @param [props.style] 컴포넌트에 적용할 인라인 스타일
 * @param [props.speed] 애니메이션 재생 속도
 * @param [props.keepLastFrame] 애니메이션 종료 시 마지막 프레임 유지 여부
 */
export function LottiePlayer({
  src,
  autoplay,
  loop = true,
  className,
  style,
  ...rest
}: LottiePlayerProps) {
  const [mounted, setMounted] = useState(false);
  const [PlayerComponent, setPlayerComponent] =
    useState<ComponentType<LottiePlayerProps> | null>(null);
  const [isInChromatic, setIsInChromatic] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setMounted(true);

    // 클라이언트에서만 동적 import
    void Promise.all([
      import("@lottiefiles/react-lottie-player"),
      import("chromatic/isChromatic"),
    ])
      .then(([{ Player }, { default: isChromatic }]) => {
        if (isMounted) {
          setPlayerComponent(() => Player as ComponentType<LottiePlayerProps>);
          setIsInChromatic(isChromatic());
        }
      })
      .catch((error) => {
        console.error("[LottiePlayer] Failed to load dependencies:", error);
        throw error;
      });

    return () => {
      isMounted = false;
    };
  }, []);

  if (!mounted || !PlayerComponent) {
    return <div className={className} style={style} />;
  }

  return (
    <PlayerComponent
      src={src}
      loop={loop}
      autoplay={autoplay !== undefined ? autoplay : !isInChromatic}
      className={className}
      style={style}
      {...rest}
    />
  );
}
