module.exports = {
  apps: [
    {
      name: 'kvtm-server',
      cwd: './apps/server',
      script: 'poetry',
      args: 'run python src/main.py --env prod',
      interpreter: 'none',
      env: {
        NODE_ENV: 'production',
        FLASK_ENV: 'production'
      },
      watch: false,
      max_memory_restart: '1G',
      error_file: '../../logs/server-error.log',
      out_file: '../../logs/server-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      instances: 1,
      exec_mode: 'fork'
    },
    {
      name: 'kvtm-client',
      cwd: './apps/client',
      script: 'pnpm',
      args: 'start',
      interpreter: 'none',
      env: {
        NODE_ENV: 'production',
        PORT: '3000'
      },
      watch: false,
      max_memory_restart: '500M',
      error_file: '../../logs/client-error.log',
      out_file: '../../logs/client-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      instances: 1,
      exec_mode: 'fork'
    }
  ]
}
