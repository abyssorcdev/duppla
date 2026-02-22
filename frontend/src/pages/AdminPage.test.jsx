import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { faker } from '../test/helpers'

vi.mock('../api/admin', () => ({
  adminApi: {
    listUsers: vi.fn(),
    approveUser: vi.fn(),
    disableUser: vi.fn(),
    listLogs: vi.fn(),
  },
}))

import AdminPage from './AdminPage'
import { adminApi } from '../api/admin'

function makeAdminUser(overrides = {}) {
  return {
    id: faker.string.uuid(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
    picture: faker.image.avatar(),
    status: faker.helpers.arrayElement(['pending', 'active', 'disabled']),
    role: faker.helpers.arrayElement(['admin', 'loader', 'approver', null]),
    ...overrides,
  }
}

function makeLog(overrides = {}) {
  return {
    id: faker.number.int({ min: 1, max: 99999 }),
    timestamp: faker.date.recent().toISOString(),
    table_name: faker.helpers.arrayElement(['documents', 'jobs', 'users']),
    action: faker.helpers.arrayElement(['created', 'state_change', 'field_updated']),
    record_id: faker.string.uuid(),
    old_value: null,
    new_value: faker.lorem.word(),
    user_id: faker.internet.email(),
    ...overrides,
  }
}

function renderPage() {
  return render(
    <MemoryRouter>
      <AdminPage />
    </MemoryRouter>,
  )
}

describe('AdminPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    adminApi.listUsers.mockResolvedValue({ data: { items: [], total: 0 } })
    adminApi.listLogs.mockResolvedValue({ data: { items: [], total: 0 } })
  })

  it('renders page title and description', async () => {
    renderPage()
    expect(screen.getByText('Panel de administración')).toBeInTheDocument()
    expect(screen.getByText(/Gestiona usuarios/)).toBeInTheDocument()
  })

  it('renders tabs (Usuarios, Logs del sistema)', () => {
    renderPage()
    expect(screen.getByRole('button', { name: 'Usuarios' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Logs del sistema' })).toBeInTheDocument()
  })

  it('shows UsersTab by default', async () => {
    renderPage()
    await waitFor(() => {
      expect(adminApi.listUsers).toHaveBeenCalled()
    })
  })

  it('switches to LogsTab when clicked', async () => {
    renderPage()
    fireEvent.click(screen.getByText('Logs del sistema'))
    await waitFor(() => {
      expect(adminApi.listLogs).toHaveBeenCalled()
    })
    expect(screen.getByText('Registros de auditoría')).toBeInTheDocument()
  })

  it('switches back to UsersTab', async () => {
    renderPage()
    fireEvent.click(screen.getByRole('button', { name: 'Logs del sistema' }))
    await screen.findByText('Registros de auditoría')
    const usuariosBtns = screen.getAllByRole('button', { name: 'Usuarios' })
    const tabBtn = usuariosBtns.find((btn) => btn.className.includes('rounded-lg'))
    fireEvent.click(tabBtn)
    await waitFor(() => {
      expect(adminApi.listUsers).toHaveBeenCalled()
    })
  })

  it('highlights active tab', () => {
    renderPage()
    const usersTab = screen.getByRole('button', { name: 'Usuarios' })
    expect(usersTab.className).toContain('bg-white')
    const logsTab = screen.getByRole('button', { name: 'Logs del sistema' })
    expect(logsTab.className).not.toContain('bg-white')
  })
})

describe('UsersTab', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    adminApi.listLogs.mockResolvedValue({ data: { items: [], total: 0 } })
  })

  it('shows loading spinner while loading users', () => {
    adminApi.listUsers.mockReturnValue(new Promise(() => {}))
    renderPage()
    expect(document.querySelector('.animate-spin')).toBeInTheDocument()
  })

  it('renders users list after loading', async () => {
    const users = [makeAdminUser({ status: 'active' }), makeAdminUser({ status: 'pending' })]
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: users, total: users.length } })

    renderPage()
    for (const u of users) {
      expect(await screen.findByText(u.name)).toBeInTheDocument()
      expect(screen.getByText(u.email)).toBeInTheDocument()
    }
  })

  it('renders stats cards (Total, Pendientes, Activos)', async () => {
    const users = [
      makeAdminUser({ status: 'active' }),
      makeAdminUser({ status: 'pending' }),
      makeAdminUser({ status: 'pending' }),
    ]
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: users, total: 3 } })

    renderPage()
    await screen.findByText('Total')
    expect(screen.getByText('Pendientes')).toBeInTheDocument()
    expect(screen.getByText('Activos')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('1')).toBeInTheDocument()
  })

  it('shows user role label', async () => {
    const user = makeAdminUser({ status: 'active', role: 'admin' })
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [user], total: 1 } })

    renderPage()
    await screen.findByText(user.name)
    const roleCells = document.querySelectorAll('td')
    const roleCell = Array.from(roleCells).find((td) => td.textContent === 'Administrador')
    expect(roleCell).toBeTruthy()
  })

  it('shows "Sin asignar" when role is null', async () => {
    const user = makeAdminUser({ status: 'pending', role: null })
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [user], total: 1 } })

    renderPage()
    expect(await screen.findByText('Sin asignar')).toBeInTheDocument()
  })

  it('shows status labels for users', async () => {
    const users = [
      makeAdminUser({ status: 'active' }),
      makeAdminUser({ status: 'pending' }),
      makeAdminUser({ status: 'disabled' }),
    ]
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: users, total: 3 } })

    renderPage()
    await screen.findByText(users[0].name)
    expect(screen.getAllByText('Activo').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('Pendiente').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('Deshabilitado').length).toBeGreaterThanOrEqual(1)
  })

  it('approves a user with selected role', async () => {
    const user = makeAdminUser({ status: 'pending', role: null })
    adminApi.listUsers
      .mockResolvedValueOnce({ data: { items: [user], total: 1 } })
      .mockResolvedValueOnce({ data: { items: [{ ...user, status: 'active', role: 'loader' }], total: 1 } })
    adminApi.approveUser.mockResolvedValueOnce({})

    renderPage()
    await screen.findByText(user.name)

    const select = screen.getByDisplayValue('— Seleccionar rol —')
    fireEvent.change(select, { target: { value: 'loader' } })
    fireEvent.click(screen.getByText('Aprobar'))

    await waitFor(() => {
      expect(adminApi.approveUser).toHaveBeenCalledWith(user.id, 'loader')
    })
  })

  it('disables an active user', async () => {
    const user = makeAdminUser({ status: 'active', role: 'loader' })
    adminApi.listUsers
      .mockResolvedValueOnce({ data: { items: [user], total: 1 } })
      .mockResolvedValueOnce({ data: { items: [{ ...user, status: 'disabled' }], total: 1 } })
    adminApi.disableUser.mockResolvedValueOnce({})

    renderPage()
    fireEvent.click(await screen.findByText('Deshabilitar'))

    await waitFor(() => {
      expect(adminApi.disableUser).toHaveBeenCalledWith(user.id)
    })
  })

  it('shows "Cambiar rol" button for active users', async () => {
    const user = makeAdminUser({ status: 'active', role: 'approver' })
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [user], total: 1 } })

    renderPage()
    expect(await screen.findByText('Cambiar rol')).toBeInTheDocument()
  })

  it('shows "Rehabilitar" button for disabled users', async () => {
    const user = makeAdminUser({ status: 'disabled', role: 'loader' })
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [user], total: 1 } })

    renderPage()
    expect(await screen.findByText('Rehabilitar')).toBeInTheDocument()
  })

  it('rehabilitates a disabled user with selected role', async () => {
    const user = makeAdminUser({ status: 'disabled', role: null })
    adminApi.listUsers
      .mockResolvedValueOnce({ data: { items: [user], total: 1 } })
      .mockResolvedValueOnce({ data: { items: [{ ...user, status: 'active', role: 'approver' }], total: 1 } })
    adminApi.approveUser.mockResolvedValueOnce({})

    renderPage()
    await screen.findByText(user.name)

    const selects = screen.getAllByDisplayValue('— Seleccionar rol —')
    fireEvent.change(selects[0], { target: { value: 'approver' } })
    fireEvent.click(screen.getByText('Rehabilitar'))

    await waitFor(() => {
      expect(adminApi.approveUser).toHaveBeenCalledWith(user.id, 'approver')
    })
  })

  it('disabled users have no Deshabilitar button', async () => {
    const user = makeAdminUser({ status: 'disabled', role: null })
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [user], total: 1 } })

    renderPage()
    await screen.findByText(user.name)
    expect(screen.queryByText('Deshabilitar')).not.toBeInTheDocument()
  })

  it('filter buttons filter users by status', async () => {
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [], total: 0 } })

    renderPage()
    await waitFor(() => expect(adminApi.listUsers).toHaveBeenCalledTimes(1))

    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [], total: 0 } })
    const allPendingBtns = screen.getAllByText('Pendiente')
    const pendingFilterBtn = allPendingBtns.find((el) => el.tagName === 'BUTTON')
    fireEvent.click(pendingFilterBtn)

    await waitFor(() => {
      expect(adminApi.listUsers).toHaveBeenCalledWith({ status: 'pending' })
    })
  })

  it('"Todos" filter passes no status', async () => {
    adminApi.listUsers.mockResolvedValue({ data: { items: [], total: 0 } })

    renderPage()
    await waitFor(() => expect(adminApi.listUsers).toHaveBeenCalledTimes(1))

    const allPendingBtns = screen.getAllByText('Pendiente')
    fireEvent.click(allPendingBtns.find((el) => el.tagName === 'BUTTON'))
    await waitFor(() => expect(adminApi.listUsers).toHaveBeenCalledTimes(2))

    const allTodosBtns = screen.getAllByText('Todos')
    fireEvent.click(allTodosBtns.find((el) => el.tagName === 'BUTTON'))
    await waitFor(() => {
      expect(adminApi.listUsers).toHaveBeenLastCalledWith({})
    })
  })

  it('shows error when listUsers fails', async () => {
    adminApi.listUsers.mockRejectedValueOnce({
      response: { data: { detail: 'No autorizado' } },
    })

    renderPage()
    expect(await screen.findByText('No autorizado')).toBeInTheDocument()
  })

  it('shows fallback error message when no detail', async () => {
    adminApi.listUsers.mockRejectedValueOnce(new Error('network'))

    renderPage()
    expect(await screen.findByText('Error al cargar usuarios')).toBeInTheDocument()
  })

  it('shows error when approveUser fails', async () => {
    const user = makeAdminUser({ status: 'pending', role: null })
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [user], total: 1 } })
    adminApi.approveUser.mockRejectedValueOnce({
      response: { data: { detail: 'Rol inválido' } },
    })

    renderPage()
    await screen.findByText(user.name)
    fireEvent.change(screen.getByDisplayValue('— Seleccionar rol —'), { target: { value: 'admin' } })
    fireEvent.click(screen.getByText('Aprobar'))

    expect(await screen.findByText('Rol inválido')).toBeInTheDocument()
  })

  it('shows fallback error when approveUser fails without detail', async () => {
    const user = makeAdminUser({ status: 'pending', role: null })
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [user], total: 1 } })
    adminApi.approveUser.mockRejectedValueOnce(new Error('boom'))

    renderPage()
    await screen.findByText(user.name)
    fireEvent.change(screen.getByDisplayValue('— Seleccionar rol —'), { target: { value: 'admin' } })
    fireEvent.click(screen.getByText('Aprobar'))

    expect(await screen.findByText('Error al aprobar usuario')).toBeInTheDocument()
  })

  it('shows error when disableUser fails', async () => {
    const user = makeAdminUser({ status: 'active', role: 'loader' })
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [user], total: 1 } })
    adminApi.disableUser.mockRejectedValueOnce({
      response: { data: { detail: 'No se puede deshabilitar' } },
    })

    renderPage()
    fireEvent.click(await screen.findByText('Deshabilitar'))

    expect(await screen.findByText('No se puede deshabilitar')).toBeInTheDocument()
  })

  it('shows fallback error when disableUser fails without detail', async () => {
    const user = makeAdminUser({ status: 'active', role: 'loader' })
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [user], total: 1 } })
    adminApi.disableUser.mockRejectedValueOnce(new Error('boom'))

    renderPage()
    fireEvent.click(await screen.findByText('Deshabilitar'))

    expect(await screen.findByText('Error al deshabilitar usuario')).toBeInTheDocument()
  })

  it('shows empty state when no users match filter', async () => {
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [], total: 0 } })

    renderPage()
    expect(await screen.findByText(/No hay usuarios/)).toBeInTheDocument()
  })

  it('empty state includes filter label when filtering', async () => {
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [], total: 0 } })
    renderPage()
    await screen.findByText(/No hay usuarios/)

    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [], total: 0 } })
    const allActivoBtns = screen.getAllByText('Activo')
    fireEvent.click(allActivoBtns.find((el) => el.tagName === 'BUTTON'))

    await waitFor(() => {
      expect(screen.getByText(/con estado "Activo"/)).toBeInTheDocument()
    })
  })

  it('falls back to raw status value for unknown user status', async () => {
    const user = makeAdminUser({ status: 'frozen_xyz' })
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [user], total: 1 } })

    renderPage()
    expect(await screen.findByText('frozen_xyz')).toBeInTheDocument()
  })

  it('approve button is disabled when no role selected', async () => {
    const user = makeAdminUser({ status: 'pending', role: null })
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [user], total: 1 } })

    renderPage()
    await screen.findByText(user.name)
    const approveBtn = screen.getByRole('button', { name: 'Aprobar' })
    expect(approveBtn).toBeDisabled()
  })

  it('shows user avatar fallback when no picture', async () => {
    const user = makeAdminUser({ status: 'active', role: 'admin', picture: null, name: 'Zxytest User' })
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [user], total: 1 } })

    renderPage()
    await screen.findByText('Zxytest User')
    expect(screen.getByText('Z')).toBeInTheDocument()
    expect(document.querySelector('img')).not.toBeInTheDocument()
  })

  it('shows user avatar image when picture exists', async () => {
    const pic = 'https://example.com/avatar.png'
    const user = makeAdminUser({ status: 'active', role: 'admin', picture: pic })
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [user], total: 1 } })

    renderPage()
    await screen.findByText(user.name)
    expect(document.querySelector(`img[src="${pic}"]`)).toBeInTheDocument()
  })

  it('shows "Guardando..." while approving', async () => {
    const user = makeAdminUser({ status: 'pending', role: null })
    adminApi.listUsers.mockResolvedValueOnce({ data: { items: [user], total: 1 } })
    adminApi.approveUser.mockReturnValue(new Promise(() => {}))

    renderPage()
    await screen.findByText(user.name)
    const selects = screen.getAllByDisplayValue('— Seleccionar rol —')
    fireEvent.change(selects[0], { target: { value: 'admin' } })
    fireEvent.click(screen.getByRole('button', { name: 'Aprobar' }))

    expect(await screen.findByText('Guardando...')).toBeInTheDocument()
  })
})

describe('LogsTab', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    adminApi.listUsers.mockResolvedValue({ data: { items: [], total: 0 } })
  })

  function switchToLogs() {
    fireEvent.click(screen.getByRole('button', { name: 'Logs del sistema' }))
  }

  it('shows loading spinner while loading logs', async () => {
    adminApi.listLogs.mockReturnValue(new Promise(() => {}))

    renderPage()
    switchToLogs()
    await waitFor(() => {
      expect(document.querySelector('.animate-spin')).toBeInTheDocument()
    })
  })

  it('renders logs list after loading', async () => {
    const logs = [makeLog(), makeLog()]
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: logs, total: logs.length } })

    renderPage()
    switchToLogs()

    for (const log of logs) {
      expect(await screen.findByText(log.new_value)).toBeInTheDocument()
    }
  })

  it('shows total entries count', async () => {
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [makeLog()], total: 42 } })

    renderPage()
    switchToLogs()

    expect(await screen.findByText('42 entradas')).toBeInTheDocument()
  })

  it('renders table filter buttons', async () => {
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [], total: 0 } })

    renderPage()
    switchToLogs()

    await screen.findByText('Registros de auditoría')
    expect(screen.getByText('Todas las tablas')).toBeInTheDocument()
    expect(screen.getByText('Documentos')).toBeInTheDocument()
    expect(screen.getByText('Jobs')).toBeInTheDocument()
  })

  it('renders action filter buttons', async () => {
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [], total: 0 } })

    renderPage()
    switchToLogs()

    await screen.findByText('Registros de auditoría')
    expect(screen.getByText('Todas las acciones')).toBeInTheDocument()
    expect(screen.getByText('Creación')).toBeInTheDocument()
    expect(screen.getByText('Cambio de estado')).toBeInTheDocument()
    expect(screen.getByText('Campo editado')).toBeInTheDocument()
  })

  it('filters by table name', async () => {
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [], total: 0 } })

    renderPage()
    switchToLogs()
    await screen.findByText('Registros de auditoría')

    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [], total: 0 } })
    fireEvent.click(screen.getByText('Documentos'))

    await waitFor(() => {
      expect(adminApi.listLogs).toHaveBeenLastCalledWith(
        expect.objectContaining({ table_name: 'documents' }),
      )
    })
  })

  it('filters by action', async () => {
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [], total: 0 } })

    renderPage()
    switchToLogs()
    await screen.findByText('Registros de auditoría')

    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [], total: 0 } })
    fireEvent.click(screen.getByText('Creación'))

    await waitFor(() => {
      expect(adminApi.listLogs).toHaveBeenLastCalledWith(
        expect.objectContaining({ action: 'created' }),
      )
    })
  })

  it('shows pagination when total > LIMIT (50)', async () => {
    const logs = Array.from({ length: 50 }, () => makeLog())
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: logs, total: 120 } })

    renderPage()
    switchToLogs()

    expect(await screen.findByText('1–50 de 120')).toBeInTheDocument()
    expect(screen.getByText('Siguiente')).toBeInTheDocument()
    expect(screen.getByText('Anterior')).toBeInTheDocument()
  })

  it('Anterior button is disabled on first page', async () => {
    const logs = Array.from({ length: 50 }, () => makeLog())
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: logs, total: 120 } })

    renderPage()
    switchToLogs()

    expect(await screen.findByText('Anterior')).toBeDisabled()
  })

  it('clicking Anterior goes to previous page', async () => {
    const logs = Array.from({ length: 50 }, () => makeLog())
    adminApi.listLogs
      .mockResolvedValueOnce({ data: { items: logs, total: 120 } })

    renderPage()
    switchToLogs()
    await screen.findByText('1–50 de 120')

    adminApi.listLogs.mockResolvedValueOnce({ data: { items: logs, total: 120 } })
    fireEvent.click(screen.getByText('Siguiente'))

    await waitFor(() => {
      expect(adminApi.listLogs).toHaveBeenLastCalledWith(expect.objectContaining({ skip: 50 }))
    })

    adminApi.listLogs.mockResolvedValueOnce({ data: { items: logs, total: 120 } })
    fireEvent.click(screen.getByText('Anterior'))

    await waitFor(() => {
      expect(adminApi.listLogs).toHaveBeenLastCalledWith(expect.objectContaining({ skip: 0 }))
    })
  })

  it('clicking Siguiente advances page', async () => {
    const logs = Array.from({ length: 50 }, () => makeLog())
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: logs, total: 120 } })

    renderPage()
    switchToLogs()
    await screen.findByText('1–50 de 120')

    adminApi.listLogs.mockResolvedValueOnce({ data: { items: logs, total: 120 } })
    fireEvent.click(screen.getByText('Siguiente'))

    await waitFor(() => {
      expect(adminApi.listLogs).toHaveBeenLastCalledWith(
        expect.objectContaining({ skip: 50, limit: 50 }),
      )
    })
  })

  it('Siguiente disabled on last page', async () => {
    const logs = Array.from({ length: 20 }, () => makeLog())
    adminApi.listLogs
      .mockResolvedValueOnce({ data: { items: logs, total: 70 } })

    renderPage()
    switchToLogs()
    await screen.findByText('1–50 de 70')

    adminApi.listLogs.mockResolvedValueOnce({ data: { items: logs, total: 70 } })
    fireEvent.click(screen.getByText('Siguiente'))

    await waitFor(() => {
      expect(screen.getByText('Siguiente')).toBeDisabled()
    })
  })

  it('does not render pagination when total <= LIMIT', async () => {
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [makeLog()], total: 5 } })

    renderPage()
    switchToLogs()
    await screen.findByText('Registros de auditoría')
    expect(screen.queryByText('Siguiente')).not.toBeInTheDocument()
  })

  it('shows error when listLogs fails', async () => {
    adminApi.listLogs.mockRejectedValueOnce({
      response: { data: { detail: 'Permiso denegado' } },
    })

    renderPage()
    switchToLogs()

    expect(await screen.findByText('Permiso denegado')).toBeInTheDocument()
  })

  it('shows fallback error when no detail', async () => {
    adminApi.listLogs.mockRejectedValueOnce(new Error('network'))

    renderPage()
    switchToLogs()

    expect(await screen.findByText('Error al cargar logs')).toBeInTheDocument()
  })

  it('shows empty state when no logs', async () => {
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [], total: 0 } })

    renderPage()
    switchToLogs()

    expect(await screen.findByText('No hay registros.')).toBeInTheDocument()
  })

  it('renders log row with old_value and new_value showing transition', async () => {
    const log = makeLog({ old_value: 'draft', new_value: 'pending' })
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [log], total: 1 } })

    renderPage()
    switchToLogs()

    expect(await screen.findByText('draft')).toBeInTheDocument()
    expect(screen.getByText('pending')).toBeInTheDocument()
  })

  it('renders log row with only new_value', async () => {
    const log = makeLog({ old_value: null, new_value: 'created' })
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [log], total: 1 } })

    renderPage()
    switchToLogs()

    expect(await screen.findByText('created')).toBeInTheDocument()
  })

  it('renders log row with only old_value', async () => {
    const log = makeLog({ old_value: 'removed', new_value: null })
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [log], total: 1 } })

    renderPage()
    switchToLogs()

    expect(await screen.findByText('removed')).toBeInTheDocument()
  })

  it('renders "—" when both old_value and new_value are null', async () => {
    const log = makeLog({ old_value: null, new_value: null })
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [log], total: 1 } })

    renderPage()
    switchToLogs()

    await screen.findByText('Registros de auditoría')
    expect(screen.getByText('—')).toBeInTheDocument()
  })

  it('renders link to document for documents table_name', async () => {
    const recordId = faker.number.int({ min: 1, max: 999 }).toString()
    const log = makeLog({ table_name: 'documents', record_id: recordId })
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [log], total: 1 } })

    renderPage()
    switchToLogs()

    const link = await screen.findByText(`#${recordId}`)
    expect(link.closest('a')).toHaveAttribute('href', `/documents/${recordId}`)
  })

  it('renders truncated record_id for non-documents table_name', async () => {
    const recordId = faker.string.uuid()
    const log = makeLog({ table_name: 'users', record_id: recordId })
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [log], total: 1 } })

    renderPage()
    switchToLogs()

    expect(await screen.findByText(`${recordId.slice(0, 8)}…`)).toBeInTheDocument()
  })

  it('renders "sistema" when user_id is null', async () => {
    const log = makeLog({ user_id: null })
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [log], total: 1 } })

    renderPage()
    switchToLogs()

    expect(await screen.findByText('sistema')).toBeInTheDocument()
  })

  it('renders user_id when present', async () => {
    const userId = faker.internet.email()
    const log = makeLog({ user_id: userId })
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [log], total: 1 } })

    renderPage()
    switchToLogs()

    expect(await screen.findByText(userId)).toBeInTheDocument()
  })

  it('renders action labels correctly', async () => {
    const log = makeLog({ action: 'state_change' })
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [log], total: 1 } })

    renderPage()
    switchToLogs()

    expect(await screen.findByText('Cambio de estado')).toBeInTheDocument()
  })

  it('falls back to raw action value for unknown actions', async () => {
    const log = makeLog({ action: 'custom_action' })
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [log], total: 1 } })

    renderPage()
    switchToLogs()

    expect(await screen.findByText('custom_action')).toBeInTheDocument()
  })

  it('falls back to raw table_name for unknown tables', async () => {
    const log = makeLog({ table_name: 'custom_table', record_id: faker.string.uuid() })
    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [log], total: 1 } })

    renderPage()
    switchToLogs()

    expect(await screen.findByText('custom_table')).toBeInTheDocument()
  })

  it('resets page to 0 when changing table filter', async () => {
    const logs = Array.from({ length: 50 }, () => makeLog())
    adminApi.listLogs
      .mockResolvedValueOnce({ data: { items: logs, total: 120 } })

    renderPage()
    switchToLogs()
    await screen.findByText('1–50 de 120')

    adminApi.listLogs.mockResolvedValueOnce({ data: { items: logs, total: 120 } })
    fireEvent.click(screen.getByText('Siguiente'))

    await waitFor(() => {
      expect(adminApi.listLogs).toHaveBeenLastCalledWith(expect.objectContaining({ skip: 50 }))
    })

    adminApi.listLogs.mockResolvedValueOnce({ data: { items: logs, total: 60 } })
    const docsBtns = screen.getAllByText('Documentos')
    fireEvent.click(docsBtns.find((el) => el.tagName === 'BUTTON'))

    await waitFor(() => {
      expect(adminApi.listLogs).toHaveBeenLastCalledWith(
        expect.objectContaining({ skip: 0, table_name: 'documents' }),
      )
    })
  })

  it('resets page to 0 when changing action filter', async () => {
    const logs = Array.from({ length: 50 }, () => makeLog())
    adminApi.listLogs
      .mockResolvedValueOnce({ data: { items: logs, total: 120 } })

    renderPage()
    switchToLogs()
    await screen.findByText('1–50 de 120')

    adminApi.listLogs.mockResolvedValueOnce({ data: { items: logs, total: 120 } })
    fireEvent.click(screen.getByText('Siguiente'))

    await waitFor(() => {
      expect(adminApi.listLogs).toHaveBeenLastCalledWith(expect.objectContaining({ skip: 50 }))
    })

    adminApi.listLogs.mockResolvedValueOnce({ data: { items: [], total: 0 } })
    const creacionBtns = screen.getAllByText('Creación')
    fireEvent.click(creacionBtns.find((el) => el.tagName === 'BUTTON'))

    await waitFor(() => {
      expect(adminApi.listLogs).toHaveBeenLastCalledWith(
        expect.objectContaining({ skip: 0, action: 'created' }),
      )
    })
  })
})
