import s from './LoadingDots.module.css';
import cn from 'classnames';

const LoadingDots: React.FC = () => {
  return (
    <span className={s.root} data-cy-id="loadingDots">
      <span className={s.dot} key={`dot_1`}></span>
      <span className={s.dot} key={`dot_2`}></span>
      <span className={s.dot} key={`dot_3`}></span>
    </span>
  );
};

export const LoadingDotsFlex: React.FC = () => {
  return (
    <span
      className={cn(s.root, 'flex h-full w-full justify-center')}
      data-cy-id="loadingDots"
    >
      <span className={s.dot} key={`dot_1`}></span>
      <span className={s.dot} key={`dot_2`}></span>
      <span className={s.dot} key={`dot_3`}></span>
    </span>
  );
};

export const LoadingDotsBigFlex: React.FC = () => {
  return (
    <span
      className={cn(s.root, 'flex h-full w-full justify-center')}
      data-cy-id="loadingDots"
    >
      <span className={s.dotBig} key={`dot_1`}></span>
      <span className={s.dotBig} key={`dot_2`}></span>
      <span className={s.dotBig} key={`dot_3`}></span>
    </span>
  );
};

export default LoadingDots;