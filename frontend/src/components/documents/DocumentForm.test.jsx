import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import DocumentForm from './DocumentForm'
import { faker } from '../../test/helpers'

function getControl(labelText) {
  const label = screen.getByText(labelText, { exact: false, selector: 'label' })
  const wrapper = label.parentElement
  return wrapper.querySelector('select, input, textarea')
}

describe('DocumentForm', () => {
  let onSubmit

  beforeEach(() => {
    onSubmit = vi.fn()
  })

  const renderForm = (props = {}) =>
    render(<DocumentForm onSubmit={onSubmit} loading={false} {...props} />)

  it('renders all basic form fields', () => {
    renderForm()
    expect(getControl('Tipo de documento')).toBeInTheDocument()
    expect(getControl('Monto')).toBeInTheDocument()
    expect(getControl('Creado por')).toBeInTheDocument()
  })

  it('renders metadata fields', () => {
    renderForm()
    expect(getControl('Cliente')).toBeInTheDocument()
    expect(getControl('Email')).toBeInTheDocument()
    expect(getControl('Referencia')).toBeInTheDocument()
    expect(getControl('Campos adicionales')).toBeInTheDocument()
  })

  it('renders submit button with default label', () => {
    renderForm()
    expect(screen.getByRole('button', { name: 'Guardar' })).toBeInTheDocument()
  })

  it('renders submit button with custom label', () => {
    const label = faker.lorem.word()
    renderForm({ submitLabel: label })
    expect(screen.getByRole('button', { name: label })).toBeInTheDocument()
  })

  it('shows "Guardando..." when loading', () => {
    renderForm({ loading: true })
    expect(screen.getByRole('button', { name: 'Guardando...' })).toBeDisabled()
  })

  it('defaults type to "invoice"', () => {
    renderForm()
    expect(getControl('Tipo de documento')).toHaveValue('invoice')
  })

  describe('validation errors', () => {
    it('shows "Requerido" errors when submitting empty form', () => {
      renderForm()
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      const requiredErrors = screen.getAllByText(/Requerido/)
      expect(requiredErrors.length).toBeGreaterThanOrEqual(1)
      expect(onSubmit).not.toHaveBeenCalled()
    })

    it('shows error when amount is empty', () => {
      renderForm()
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      expect(screen.getByText('Debe ser mayor a 0')).toBeInTheDocument()
    })

    it('shows error when amount is 0', () => {
      renderForm()
      fireEvent.change(getControl('Monto'), { target: { value: '0' } })
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      expect(screen.getByText('Debe ser mayor a 0')).toBeInTheDocument()
    })

    it('shows error when amount field is left empty (falsy check)', () => {
      renderForm()
      fireEvent.change(getControl('Monto'), { target: { value: '' } })
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      expect(screen.getByText('Debe ser mayor a 0')).toBeInTheDocument()
    })

    it('shows error when created_by is empty', () => {
      renderForm()
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      expect(screen.getAllByText('Requerido').length).toBeGreaterThanOrEqual(1)
    })

    it('shows error when created_by is only whitespace', () => {
      renderForm()
      fireEvent.change(getControl('Creado por'), { target: { value: '   ' } })
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      expect(onSubmit).not.toHaveBeenCalled()
    })

    it('shows error when metadata_client is empty', () => {
      renderForm()
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      expect(screen.getAllByText(/Requerido/).length).toBeGreaterThanOrEqual(1)
    })

    it('shows error when metadata_email is empty', () => {
      renderForm()
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      expect(screen.getAllByText(/Requerido/).length).toBeGreaterThanOrEqual(1)
    })

    it('shows error for invalid JSON in metadata_extra', () => {
      renderForm()
      fireEvent.change(getControl('Campos adicionales'), {
        target: { value: '{ invalid json' },
      })
      fireEvent.change(getControl('Monto'), { target: { value: '100' } })
      fireEvent.change(getControl('Creado por'), { target: { value: 'user' } })
      fireEvent.change(getControl('Cliente'), { target: { value: 'Acme' } })
      fireEvent.change(getControl('Email'), { target: { value: 'a@b.com' } })
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      expect(screen.getByText('JSON inválido — verifica la sintaxis')).toBeInTheDocument()
      expect(onSubmit).not.toHaveBeenCalled()
    })

    it('shows error when metadata_extra is an array JSON', () => {
      renderForm()
      fireEvent.change(getControl('Campos adicionales'), {
        target: { value: '[1, 2, 3]' },
      })
      fireEvent.change(getControl('Monto'), { target: { value: '100' } })
      fireEvent.change(getControl('Creado por'), { target: { value: 'user' } })
      fireEvent.change(getControl('Cliente'), { target: { value: 'Acme' } })
      fireEvent.change(getControl('Email'), { target: { value: 'a@b.com' } })
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      expect(
        screen.getByText('Debe ser un objeto JSON, ej: { "clave": "valor" }')
      ).toBeInTheDocument()
      expect(onSubmit).not.toHaveBeenCalled()
    })

    it('clears field error when user changes that field', () => {
      renderForm()
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      expect(screen.getByText('Debe ser mayor a 0')).toBeInTheDocument()
      fireEvent.change(getControl('Monto'), { target: { value: '500' } })
      expect(screen.queryByText('Debe ser mayor a 0')).not.toBeInTheDocument()
    })
  })

  describe('successful submission', () => {
    const fillValidForm = () => {
      fireEvent.change(getControl('Tipo de documento'), { target: { value: 'receipt' } })
      fireEvent.change(getControl('Monto'), { target: { value: '12345.67' } })
      fireEvent.change(getControl('Creado por'), { target: { value: 'tester@co.com' } })
      fireEvent.change(getControl('Cliente'), { target: { value: 'Acme Corp' } })
      fireEvent.change(getControl('Email'), { target: { value: 'pay@acme.com' } })
    }

    it('submits correct payload without optional fields', () => {
      renderForm()
      fillValidForm()
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      expect(onSubmit).toHaveBeenCalledWith({
        type: 'receipt',
        amount: 12345.67,
        created_by: 'tester@co.com',
        metadata: {
          client: 'Acme Corp',
          email: 'pay@acme.com',
        },
      })
    })

    it('includes reference in metadata when provided', () => {
      renderForm()
      fillValidForm()
      const ref = faker.string.alphanumeric(10)
      fireEvent.change(getControl('Referencia'), { target: { value: ref } })
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          metadata: expect.objectContaining({ reference: ref }),
        })
      )
    })

    it('does not include reference in metadata when empty', () => {
      renderForm()
      fillValidForm()
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      const payload = onSubmit.mock.calls[0][0]
      expect(payload.metadata).not.toHaveProperty('reference')
    })

    it('merges metadata_extra into metadata', () => {
      renderForm()
      fillValidForm()
      fireEvent.change(getControl('Campos adicionales'), {
        target: { value: '{"region": "Bogotá"}' },
      })
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          metadata: expect.objectContaining({ region: 'Bogotá' }),
        })
      )
    })

    it('trims created_by and metadata fields', () => {
      renderForm()
      fireEvent.change(getControl('Tipo de documento'), { target: { value: 'invoice' } })
      fireEvent.change(getControl('Monto'), { target: { value: '100' } })
      fireEvent.change(getControl('Creado por'), { target: { value: '  user  ' } })
      fireEvent.change(getControl('Cliente'), { target: { value: '  Client  ' } })
      fireEvent.change(getControl('Email'), { target: { value: '  e@x.com  ' } })
      fireEvent.change(getControl('Referencia'), { target: { value: '  REF-1  ' } })
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      const payload = onSubmit.mock.calls[0][0]
      expect(payload.created_by).toBe('user')
      expect(payload.metadata.client).toBe('Client')
      expect(payload.metadata.email).toBe('e@x.com')
      expect(payload.metadata.reference).toBe('REF-1')
    })
  })

  describe('initial values', () => {
    it('populates form from initial prop', () => {
      const initial = {
        type: 'voucher',
        amount: 999,
        created_by: 'admin@test.com',
        metadata: {
          client: 'TestCo',
          email: 'tc@test.com',
          reference: 'REF-X',
        },
      }
      renderForm({ initial })
      expect(getControl('Tipo de documento')).toHaveValue('voucher')
      expect(getControl('Monto')).toHaveValue(999)
      expect(getControl('Creado por')).toHaveValue('admin@test.com')
      expect(getControl('Cliente')).toHaveValue('TestCo')
      expect(getControl('Email')).toHaveValue('tc@test.com')
      expect(getControl('Referencia')).toHaveValue('REF-X')
    })

    it('populates metadata_extra from non-reserved metadata keys', () => {
      const initial = {
        type: 'invoice',
        amount: 500,
        created_by: 'u',
        metadata: {
          client: 'C',
          email: 'e@e.com',
          region: 'Bogotá',
          dept: 'Sales',
        },
      }
      renderForm({ initial })
      const textarea = getControl('Campos adicionales')
      const parsed = JSON.parse(textarea.value)
      expect(parsed).toEqual({ region: 'Bogotá', dept: 'Sales' })
    })

    it('leaves metadata_extra empty when metadata has only reserved keys', () => {
      const initial = {
        type: 'invoice',
        amount: 500,
        created_by: 'u',
        metadata: { client: 'C', email: 'e@e.com', reference: 'R' },
      }
      renderForm({ initial })
      expect(getControl('Campos adicionales')).toHaveValue('')
    })

    it('handles null metadata gracefully', () => {
      const initial = { type: 'invoice', amount: 100, created_by: 'u', metadata: null }
      renderForm({ initial })
      expect(getControl('Cliente')).toHaveValue('')
      expect(getControl('Campos adicionales')).toHaveValue('')
    })

    it('handles undefined metadata gracefully', () => {
      const initial = { type: 'invoice', amount: 100, created_by: 'u' }
      renderForm({ initial })
      expect(getControl('Cliente')).toHaveValue('')
    })
  })

  describe('metadata_extra hint text', () => {
    it('shows hint text when there is no metadata_extra error', () => {
      renderForm()
      expect(screen.getByText(/Se combina con los campos anteriores/)).toBeInTheDocument()
    })

    it('hides hint text when metadata_extra has error', () => {
      renderForm()
      fireEvent.change(getControl('Campos adicionales'), {
        target: { value: 'bad json' },
      })
      fireEvent.change(getControl('Monto'), { target: { value: '100' } })
      fireEvent.change(getControl('Creado por'), { target: { value: 'u' } })
      fireEvent.change(getControl('Cliente'), { target: { value: 'c' } })
      fireEvent.change(getControl('Email'), { target: { value: 'e@e.com' } })
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      expect(screen.queryByText(/Se combina con los campos anteriores/)).not.toBeInTheDocument()
    })
  })

  describe('empty metadata_extra is not parsed', () => {
    it('submits without extra metadata when textarea is blank', () => {
      renderForm()
      fireEvent.change(getControl('Tipo de documento'), { target: { value: 'invoice' } })
      fireEvent.change(getControl('Monto'), { target: { value: '100' } })
      fireEvent.change(getControl('Creado por'), { target: { value: 'u' } })
      fireEvent.change(getControl('Cliente'), { target: { value: 'c' } })
      fireEvent.change(getControl('Email'), { target: { value: 'e@e.com' } })
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      const payload = onSubmit.mock.calls[0][0]
      expect(payload.metadata).toEqual({ client: 'c', email: 'e@e.com' })
    })

    it('submits without extra metadata when textarea is whitespace only', () => {
      renderForm()
      fireEvent.change(getControl('Tipo de documento'), { target: { value: 'invoice' } })
      fireEvent.change(getControl('Monto'), { target: { value: '100' } })
      fireEvent.change(getControl('Creado por'), { target: { value: 'u' } })
      fireEvent.change(getControl('Cliente'), { target: { value: 'c' } })
      fireEvent.change(getControl('Email'), { target: { value: 'e@e.com' } })
      fireEvent.change(getControl('Campos adicionales'), { target: { value: '   ' } })
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      const payload = onSubmit.mock.calls[0][0]
      expect(payload.metadata).toEqual({ client: 'c', email: 'e@e.com' })
    })
  })

  describe('type validation', () => {
    it('shows error when type is cleared to empty', () => {
      renderForm()
      fireEvent.change(getControl('Tipo de documento'), { target: { value: '' } })
      fireEvent.change(getControl('Monto'), { target: { value: '100' } })
      fireEvent.change(getControl('Creado por'), { target: { value: 'u' } })
      fireEvent.change(getControl('Cliente'), { target: { value: 'c' } })
      fireEvent.change(getControl('Email'), { target: { value: 'e@e.com' } })
      fireEvent.click(screen.getByRole('button', { name: 'Guardar' }))
      expect(screen.getByText('Requerido')).toBeInTheDocument()
      expect(onSubmit).not.toHaveBeenCalled()
    })
  })
})
