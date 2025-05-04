import { Schedule } from '../base/schedule';
/**
 * Inline Edit interactions
 */
export declare class InlineEdit {
    private parent;
    private inlineInputEle;
    constructor(parent: Schedule);
    private inlineEdit;
    private cellEdit;
    private eventEdit;
    private createVerticalViewInline;
    private createMonthViewInline;
    private createTimelineViewInline;
    private getEventDaysCount;
    private generateEventData;
    documentClick(target: HTMLInputElement): void;
    inlineCrudActions(target: HTMLTableCellElement): void;
    createInlineAppointmentElement(inlineData?: Record<string, any>): HTMLElement;
    removeInlineAppointmentElement(): void;
    getInlineElement(): HTMLInputElement | null;
    destroy(): void;
}
