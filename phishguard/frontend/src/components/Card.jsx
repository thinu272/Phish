import React from 'react'

/** Dashboard card on a 12-column grid. span = 3|4|5|6|7|8|12. */
export default function Card({ title, note, span = 6, children }) {
  return (
    <div className={`card s${span}`}>
      <h3 dangerouslySetInnerHTML={{ __html: title }} />
      {note && <div className="note">{note}</div>}
      {children}
    </div>
  )
}

export const Grid = ({ children }) => <div className="grid">{children}</div>
export const Section = ({ children }) => <div className="sec">{children}</div>
