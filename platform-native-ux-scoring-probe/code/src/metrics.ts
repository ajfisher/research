import { DomMetricsCollector } from './types';

export const collectDomMetrics: DomMetricsCollector = async page => {
  return page.evaluate(() => {
    const q = document.querySelectorAll.bind(document);

    const anchors = q('a[href]');
    const nonSemanticClickables = Array.from(
      q('[onclick], [role="button"], [role="link"]')
    ).filter((el: Element) => !['A', 'BUTTON', 'INPUT'].includes(el.tagName));

    const forms = q('form');
    const controls = q('input, select, textarea, button');
    const constrainedControls = Array.from(controls).filter((el: any) =>
      el.hasAttribute('required') ||
      el.hasAttribute('pattern') ||
      (el as HTMLInputElement).type === 'email' ||
      (el as HTMLInputElement).type === 'number' ||
      el.hasAttribute('min') ||
      el.hasAttribute('max')
    );

    const fauxControls = nonSemanticClickables;

    const semanticContainers = q('main, nav, header, footer, section, article');

    const inputControls = q('input, textarea, select');
    const labelledControls = Array.from(inputControls).filter((el: any) => {
      const id = el.id;
      if (el.getAttribute('aria-label') || el.getAttribute('aria-labelledby')) return true;
      if (!id) return false;
      return !!document.querySelector(`label[for="${id}"]`);
    });

    const roleButtonOrLinkNonNative = Array.from(
      q('[role="button"], [role="link"]')
    ).filter((el: Element) => !['A', 'BUTTON', 'INPUT'].includes(el.tagName));

    const hasClientRouterSignatures =
      !!document.querySelector('[data-reactroot], [data-react-helmet], [ng-version]');

    return {
      anchorCount: anchors.length,
      nonSemanticClickableCount: nonSemanticClickables.length,
      url: location.href,
      formCount: forms.length,
      controlCount: controls.length,
      constrainedControlCount: constrainedControls.length,
      fauxControlCount: fauxControls.length,
      semanticContainerCount: semanticContainers.length,
      labelledControlCount: labelledControls.length,
      roleButtonOrLinkNonNativeCount: roleButtonOrLinkNonNative.length,
      hasClientRouterSignatures,
    };
  });
};
