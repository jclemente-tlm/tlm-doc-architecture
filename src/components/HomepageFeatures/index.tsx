import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

// Cards adaptadas a la documentación del proyecto
const FeatureList = [
  {
    title: 'Lineamientos de Arquitectura',
    img: require('@site/static/img/checklist.png').default,
    description: (
      <>
        Guías prácticas que traducen los principios corporativos en reglas concretas para <b>arquitectura, desarrollo, seguridad y operabilidad</b>.<br />
        <a href="/tlm-doc-architecture/docs/fundamentos/lineamientos">Ver lineamientos</a>
      </>
    ),
  },
  {
    title: 'Estándares Técnicos',
    img: require('@site/static/img/coding.png').default,
    description: (
      <>
        Reglas técnicas obligatorias para el desarrollo consistente de servicios, desde <b>código y APIs</b> hasta <b>infraestructura, seguridad y observabilidad</b>.<br />
        <a href="/tlm-doc-architecture/docs/fundamentos/estandares">Ver estándares</a>
      </>
    ),
  },
  {
    title: 'Registros de Decisiones Arquitectónicas (ADRs)',
    img: require('@site/static/img/documentation.png').default,
    description: (
      <>
        Conoce el contexto, las alternativas evaluadas y el razonamiento detrás de las <b>decisiones de diseño</b> del ecosistema Talma.<br />
        <a href="/tlm-doc-architecture/docs/adrs">Ver ADRs</a>
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
