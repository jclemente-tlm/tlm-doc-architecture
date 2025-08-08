import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

// Cards adaptadas a la documentación del proyecto
const FeatureList = [
  {
    title: 'Lineamientos y Estándares',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        Accede a las guías de <b>nombres, código y documentación</b> para mantener la calidad y consistencia en todos los servicios.<br />
        <a href="/docs/lineamientos/intro">Ver lineamientos</a>
      </>
    ),
  },
  {
    title: 'Registros de Decisiones Arquitectónicas (ADRs)',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        Consulta las decisiones clave de arquitectura tomadas para el ecosistema Talma.<br />
        <a href="/docs/adrs/README">Ver ADRs</a>
      </>
    ),
  },
  {
    title: 'Principios y Arquitectura',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        Explora los <b>principios de arquitectura</b> y mejores prácticas para el desarrollo de servicios escalables y seguros.<br />
        <a href="/docs/lineamientos/principios-de-arquitectura/01-clean-architecture">Ver arquitectura</a>
      </>
    ),
  },
];

function Feature({title, Svg, description}: {title: string; Svg: React.ComponentType<React.ComponentProps<'svg'>>; description: ReactNode;}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
