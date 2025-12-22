"use client";

import dynamic from "next/dynamic";
import { CSSProperties, ComponentType } from "react";

export interface LottiePlayerProps {
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

/**
 * Lottie 애니메이션을 렌더링하는 재사용 가능한 컴포넌트입니다.
 * Next.js의 dynamic import를 사용하여 클라이언트 사이드에서만 렌더링됩니다.
 *
 * @param props 컴포넌트 props
 * @param props.src Lottie JSON 파일의 경로 또는 URL
 * @param [props.className] 컴포넌트에 적용할 추가 클래스 이름
 * @param [props.loop=true] 애니메이션 반복 여부
 * @param [props.autoplay] 자동 재생 여부. Chromatic 환경이 아닐 경우 기본값은 `true`입니다.
 * @param [props.style] 컴포넌트에 적용할 인라인 스타일
 * @param [props.speed] 애니메이션 재생 속도
 */
export function LottiePlayer(props: LottiePlayerProps) {
  return <DynamicLottiePlayer {...props} />;
}
