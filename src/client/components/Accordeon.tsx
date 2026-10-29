import { useId, useState, type ReactNode } from 'react';
import { Icone } from './Icone';

export interface ElementFaq {
  question: string;
  reponse: ReactNode;
  icone?: string;
  categorie?: string;
}

export function Accordeon({ elements, grand = false }: { elements: ElementFaq[]; grand?: boolean }) {
  const [ouvert, setOuvert] = useState<number | null>(null);
  const base = useId();
  return (
    <div className="space-y-space-sm">
      {elements.map((el, i) => {
        const actif = ouvert === i;
        return (
          <div key={el.question} className={`overflow-hidden bg-surface-container-lowest shadow-doux ${grand ? 'rounded-2xl p-space-md' : 'rounded-xl px-space-md py-space-sm'}`}>
            <h3>
              <button type="button" aria-expanded={actif} aria-controls={`${base}-${i}`} onClick={() => setOuvert(actif ? null : i)} className="flex w-full items-center justify-between gap-3 text-left">
                <span className="flex items-center gap-space-sm">
                  {el.icone && (
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary-container text-on-primary-container">
                      <Icone nom={el.icone} className="text-[18px]" />
                    </span>
                  )}
                  <span className="font-titre text-title-md text-on-surface">{el.question}</span>
                </span>
                <Icone nom="expand_more" className={`shrink-0 text-outline transition-transform ${actif ? 'rotate-180' : ''}`} />
              </button>
            </h3>
            <div id={`${base}-${i}`} hidden={!actif} className={`pt-space-sm font-texte text-body-md text-on-surface-variant ${el.icone ? 'md:pl-11' : ''}`}>
              {el.reponse}
            </div>
          </div>
        );
      })}
    </div>
  );
}
