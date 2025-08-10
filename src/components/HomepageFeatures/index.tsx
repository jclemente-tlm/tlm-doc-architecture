import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

// Cards adaptadas a la documentación del proyecto
const FeatureList = [
  {
    title: 'Lineamientos y Estándares',
    img: require('@site/static/img/checklist.png').default,
    description: (
      <>
        Accede a las guías de <b>nombres, código y documentación</b> para mantener la calidad y consistencia en todos los servicios.<br />
        <a href="/docs/lineamientos">Ver lineamientos</a>
      </>
    ),
  },
  {
    title: 'Registros de Decisiones Arquitectónicas (ADRs)',
    img: require('@site/static/img/documentation.png').default,
    description: (
      <>
        Consulta las decisiones clave de arquitectura tomadas para el ecosistema Talma.<br />
        <a href="/docs/adrs">Ver ADRs</a>
      </>
    ),
  },
  {
    title: 'Principios y Arquitectura',
    img: require('@site/static/img/coding.png').default,
    description: (
      <>
        Explora los <b>principios de arquitectura</b> y mejores prácticas para el desarrollo de servicios escalables y seguros.<br />
        <a href="/docs/lineamientos/principios-de-arquitectura/01-clean-architecture">Ver arquitectura</a>
      </>
    ),
  },
];

function Feature({title, img, Svg, description}: {title: string; img?: string; Svg?: React.ComponentType<React.ComponentProps<'svg'>>; description: ReactNode;}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        {Svg ? (
          <Svg className={styles.featureSvg} role="img" />
        ) : img ? (
          <img src={img} className={styles.featureSvg} alt={title} />
        ) : null}
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
