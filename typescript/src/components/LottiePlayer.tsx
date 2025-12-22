"use client";

import dynamic from "next/dynamic";
import { CSSProperties, ComponentType } from "react";

interface LottiePlayerProps {
  src: string;
  className?: string;
  loop?: boolean;
  autoplay?: boolean;
  style?: CSSProperties;
  speed?: number;
}

// 로딩 상태를 위한 플레이스홀더 컴포넌트
const LoadingPlaceholder = ({ className }: { className?: string }) => (
  <div className={className} />
);

/**
 * A reusable component for rendering Lottie animations.
 * @param {LottiePlayerProps} props - The component props.
 * @param {string} props.src - The path to the Lottie JSON file.
 * @param {string} [props.className] - Additional class names to apply to the component.
 */
const DynamicLottiePlayer = dynamic<LottiePlayerProps>(
  async () => {
    // 필요한 모듈들 임포트
    const { Player } = await import("@lottiefiles/react-lottie-player");
    const { default: isChromatic } = await import("chromatic/isChromatic");
    const isInChromatic = isChromatic();

    // 래퍼 컴포넌트 정의
    const LottiePlayerWrapper: ComponentType<LottiePlayerProps> = ({
      src,
      autoplay,
      loop = true,
      ...rest
    }) => (
      <Player
        src={src}
        loop={loop}
        autoplay={autoplay !== undefined ? autoplay : !isInChromatic}
        {...rest}
      />
    );

    // 컴포넌트 반환
    return LottiePlayerWrapper;
  },
  {
    ssr: false, // 서버 사이드 렌더링 비활성화
    loading: () => <LoadingPlaceholder />, // 로딩 중 표시할 컴포넌트
  },
);

// 컴포넌트 내보내기
export function LottiePlayer(props: LottiePlayerProps) {
  return <DynamicLottiePlayer {...props} />;
}
