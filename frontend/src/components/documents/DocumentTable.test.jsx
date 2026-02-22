import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import DocumentTable from './DocumentTable'
import { faker, makeDocument } from '../../test/helpers'

function renderTable(props = {}) {
  const defaults = {
    documents: [],
    selected: [],
    onToggle: vi.fn(),
    onToggleAll: vi.fn(),
    ...props,
  }
  return {
    ...render(
      <BrowserRouter>
        <DocumentTable {...defaults} />
      </BrowserRouter>
    ),
    props: defaults,
  }
}

describe('DocumentTable', () => {
  describe('empty state', () => {
    it('shows empty message when documents is empty', () => {
      renderTable({ documents: [] })
      expect(screen.getByText('No se encontraron documentos')).toBeInTheDocument()
    })

    it('does not render a table when documents is empty', () => {
      renderTable({ documents: [] })
      expect(screen.queryByRole('table')).not.toBeInTheDocument()
    })
  })

  describe('rendering rows', () => {
    it('renders a row for each document', () => {
      const docs = [makeDocument(), makeDocument(), makeDocument()]
      renderTable({ documents: docs })
      const rows = screen.getAllByRole('row')
      // 1 header + 3 body rows
      expect(rows.length).toBe(4)
    })

    it('displays document id with # prefix', () => {
      const doc = makeDocument({ id: 42 })
      renderTable({ documents: [doc] })
      expect(screen.getByText('#42')).toBeInTheDocument()
    })

    it('displays document type label', () => {
      const doc = makeDocument({ type: 'invoice' })
      renderTable({ documents: [doc] })
      expect(screen.getByText('Factura')).toBeInTheDocument()
    })

    it('falls back to raw type when TYPE_LABELS has no entry', () => {
      const doc = makeDocument({ type: 'unknown_type' })
      renderTable({ documents: [doc] })
      expect(screen.getByText('unknown_type')).toBeInTheDocument()
    })

    it('displays document created_by', () => {
      const createdBy = faker.internet.email()
      const doc = makeDocument({ created_by: createdBy })
      renderTable({ documents: [doc] })
      expect(screen.getByText(createdBy)).toBeInTheDocument()
    })

    it('renders a link to document detail', () => {
      const doc = makeDocument({ id: 77 })
      renderTable({ documents: [doc] })
      const link = screen.getByText('Ver →')
      expect(link.closest('a')).toHaveAttribute('href', '/documents/77')
    })
  })

  describe('selectable statuses (draft, rejected)', () => {
    it('renders checkbox for draft documents', () => {
      const doc = makeDocument({ status: 'draft' })
      renderTable({ documents: [doc] })
      const checkboxes = screen.getAllByRole('checkbox')
      expect(checkboxes.length).toBe(2) // header + row
    })

    it('renders checkbox for rejected documents', () => {
      const doc = makeDocument({ status: 'rejected' })
      renderTable({ documents: [doc] })
      const checkboxes = screen.getAllByRole('checkbox')
      expect(checkboxes.length).toBe(2)
    })

    it('does not render row checkbox for pending documents', () => {
      const doc = makeDocument({ status: 'pending' })
      renderTable({ documents: [doc] })
      const checkboxes = screen.getAllByRole('checkbox')
      expect(checkboxes.length).toBe(1) // only header checkbox
    })

    it('does not render row checkbox for approved documents', () => {
      const doc = makeDocument({ status: 'approved' })
      renderTable({ documents: [doc] })
      const checkboxes = screen.getAllByRole('checkbox')
      expect(checkboxes.length).toBe(1)
    })

    it('renders a spacer span instead of checkbox for non-selectable', () => {
      const doc = makeDocument({ status: 'approved' })
      const { container } = renderTable({ documents: [doc] })
      const spacers = container.querySelectorAll('span.w-4.h-4')
      expect(spacers.length).toBe(1)
    })
  })

  describe('toggle select/deselect', () => {
    it('calls onToggle with doc id when row checkbox is clicked', () => {
      const doc = makeDocument({ status: 'draft', id: 10 })
      const { props } = renderTable({ documents: [doc] })
      const checkboxes = screen.getAllByRole('checkbox')
      fireEvent.click(checkboxes[1]) // row checkbox
      expect(props.onToggle).toHaveBeenCalledWith(10)
    })

    it('marks row checkbox as checked when doc is selected', () => {
      const doc = makeDocument({ status: 'draft', id: 10 })
      renderTable({ documents: [doc], selected: [10] })
      const checkboxes = screen.getAllByRole('checkbox')
      expect(checkboxes[1]).toBeChecked()
    })

    it('marks row checkbox as unchecked when doc is not selected', () => {
      const doc = makeDocument({ status: 'draft', id: 10 })
      renderTable({ documents: [doc], selected: [] })
      const checkboxes = screen.getAllByRole('checkbox')
      expect(checkboxes[1]).not.toBeChecked()
    })
  })

  describe('toggleAll behavior', () => {
    it('calls onToggleAll with selectable doc ids when header checkbox is clicked', () => {
      const docs = [
        makeDocument({ status: 'draft', id: 1 }),
        makeDocument({ status: 'pending', id: 2 }),
        makeDocument({ status: 'rejected', id: 3 }),
      ]
      const { props } = renderTable({ documents: docs })
      const headerCheckbox = screen.getAllByRole('checkbox')[0]
      fireEvent.click(headerCheckbox)
      expect(props.onToggleAll).toHaveBeenCalledWith([1, 3])
    })

    it('header checkbox is checked when all selectable docs are selected', () => {
      const docs = [
        makeDocument({ status: 'draft', id: 1 }),
        makeDocument({ status: 'pending', id: 2 }),
        makeDocument({ status: 'rejected', id: 3 }),
      ]
      renderTable({ documents: docs, selected: [1, 3] })
      const headerCheckbox = screen.getAllByRole('checkbox')[0]
      expect(headerCheckbox).toBeChecked()
    })

    it('header checkbox is unchecked when not all selectable docs are selected', () => {
      const docs = [
        makeDocument({ status: 'draft', id: 1 }),
        makeDocument({ status: 'rejected', id: 3 }),
      ]
      renderTable({ documents: docs, selected: [1] })
      const headerCheckbox = screen.getAllByRole('checkbox')[0]
      expect(headerCheckbox).not.toBeChecked()
    })

    it('header checkbox is unchecked when no selectable docs exist', () => {
      const docs = [makeDocument({ status: 'approved', id: 1 })]
      renderTable({ documents: docs })
      const headerCheckbox = screen.getAllByRole('checkbox')[0]
      expect(headerCheckbox).not.toBeChecked()
    })
  })

  describe('mixed statuses', () => {
    it('renders checkboxes only for draft and rejected in a mixed list', () => {
      const docs = [
        makeDocument({ status: 'draft', id: 1 }),
        makeDocument({ status: 'pending', id: 2 }),
        makeDocument({ status: 'approved', id: 3 }),
        makeDocument({ status: 'rejected', id: 4 }),
      ]
      renderTable({ documents: docs })
      const checkboxes = screen.getAllByRole('checkbox')
      // header + 2 selectable rows
      expect(checkboxes.length).toBe(3)
    })
  })
})
